# ============================================================
# SMART ATTENDANCE SYSTEM
# BROWSER CAMERA MODULE
# ============================================================

from flask import Blueprint, jsonify, request
from pathlib import Path
from datetime import datetime
import base64
import json
import os
import threading
import time

# Load DeepFace once when the worker starts.
# This prevents the first camera request from timing out on Render.
from deepface import DeepFace

import cv2
import numpy as np

from .attendance import mark_attendance
from .train import train_model


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_DIR = BASE_DIR / "dataset"
DATABASE_DIR = BASE_DIR / "database"
MODELS_DIR = BASE_DIR / "models"

STUDENTS_FILE = DATABASE_DIR / "students.json"
CLASSIFIER_FILE = MODELS_DIR / "classifier.xml"
FACE_CASCADE_FILE = MODELS_DIR / "haarcascade_frontalface_default.xml"


DATASET_DIR.mkdir(exist_ok=True)
DATABASE_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)


# ============================================================
# BLUEPRINT
# ============================================================

browser_camera = Blueprint(
    "browser_camera",
    __name__
)


# ============================================================
# REGISTRATION SESSION
# ============================================================

registration_data = {}

registration_lock = threading.Lock()


# ============================================================
# PERFORMANCE CACHE
# ============================================================

recognizer_cache = None
recognizer_lock = threading.Lock()

# Emotion cache: DeepFace is heavy on Render, so do not run it on every frame.
emotion_cache = {}
emotion_cache_lock = threading.Lock()
EMOTION_CACHE_SECONDS = 3.0

# ============================================================
# FACE DETECTOR
# ============================================================

face_detector = cv2.CascadeClassifier(
    str(FACE_CASCADE_FILE)
)

if face_detector.empty():
    print(
        "WARNING: Haar Cascade could not be loaded:"
    )

    print(
        FACE_CASCADE_FILE
    )


# ============================================================
# LOAD / CACHE LBPH CLASSIFIER
# ============================================================

def get_cached_recognizer():
    global recognizer_cache

    with recognizer_lock:
        if recognizer_cache is not None:
            return recognizer_cache

        if not CLASSIFIER_FILE.exists():
            print("Recognition model not found:", CLASSIFIER_FILE)
            return None

        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(str(CLASSIFIER_FILE))
            recognizer_cache = recognizer
            print("LBPH classifier loaded into memory.")
            return recognizer
        except Exception as error:
            print("Classifier load error:", error)
            return None


def clear_recognizer_cache():
    global recognizer_cache
    with recognizer_lock:
        recognizer_cache = None


# ============================================================
# LOAD STUDENTS
# ============================================================

def load_students():

    if not STUDENTS_FILE.exists():
        return {}

    try:

        with open(
            STUDENTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print(
            "Students JSON error:",
            error
        )

        return {}


# ============================================================
# SAVE STUDENTS
# ============================================================

def save_students(students):

    DATABASE_DIR.mkdir(
        exist_ok=True
    )

    with open(
        STUDENTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            students,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# DECODE BROWSER IMAGE
# ============================================================

def decode_image():

    if "frame" not in request.files:

        return None

    file = request.files["frame"]

    image_bytes = file.read()

    if not image_bytes:

        return None

    array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    frame = cv2.imdecode(
        array,
        cv2.IMREAD_COLOR
    )

    return frame


# ============================================================
# START STUDENT REGISTRATION
# ============================================================

@browser_camera.route(
    "/api/browser/register/start",
    methods=["POST"]
)
def browser_register_start():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message":
                    "Registration data not received."
            }), 400

        person_id = int(
            data.get("person_id")
        )

        name = str(
            data.get("name", "")
        ).strip()

        total_photos = int(
            data.get(
                "photos",
                200
            )
        )

        if person_id <= 0:

            return jsonify({
                "success": False,
                "message":
                    "Student ID must be greater than 0."
            }), 400

        if not name:

            return jsonify({
                "success": False,
                "message":
                    "Student name is required."
            }), 400

        if total_photos < 20:

            total_photos = 20

        if total_photos > 300:

            total_photos = 300


        # ----------------------------------------------------
        # CREATE STUDENT FOLDER
        # ----------------------------------------------------

        student_folder = (
            DATASET_DIR /
            str(person_id)
        )

        if student_folder.exists():

            import shutil

            shutil.rmtree(
                student_folder
            )

        student_folder.mkdir(
            parents=True,
            exist_ok=True
        )


        # ----------------------------------------------------
        # SAVE REGISTRATION SESSION
        # ----------------------------------------------------

        with registration_lock:

            registration_data[
                person_id
            ] = {

                "name": name,

                "total_photos":
                    total_photos,

                "count": 0,

                "folder":
                    str(student_folder)

            }


        print()
        print(
            "========================================"
        )
        print(
            "BROWSER REGISTRATION STARTED"
        )
        print(
            "Student ID:",
            person_id
        )
        print(
            "Name:",
            name
        )
        print(
            "Photos:",
            total_photos
        )
        print(
            "========================================"
        )


        return jsonify({

            "success": True,

            "message":
                "Browser camera registration started.",

            "person_id":
                person_id,

            "name":
                name,

            "total_photos":
                total_photos,

            "captured":
                0

        })


    except ValueError:

        return jsonify({

            "success": False,

            "message":
                "Student ID and photo count must be numbers."

        }), 400


    except Exception as error:

        print(
            "Browser registration start error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# CAPTURE ONE BROWSER FRAME
# ============================================================

@browser_camera.route(
    "/api/browser/register/frame",
    methods=["POST"]
)
def browser_register_frame():

    try:

        person_id = int(
            request.form.get(
                "person_id"
            )
        )


        with registration_lock:

            session = registration_data.get(
                person_id
            )


        if not session:

            return jsonify({

                "success": False,

                "message":
                    "Registration session not found."

            }), 404


        if (
            session["count"]
            >=
            session["total_photos"]
        ):

            return jsonify({

                "success": True,

                "complete": True,

                "captured":
                    session["count"],

                "total_photos":
                    session["total_photos"]

            })


        frame = decode_image()


        if frame is None:

            return jsonify({

                "success": False,

                "message":
                    "Invalid camera frame."

            }), 400


        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )


        faces = face_detector.detectMultiScale(

            gray,

            scaleFactor=1.1,

            minNeighbors=6,

            minSize=(80, 80)

        )


        if len(faces) == 0:

            return jsonify({

                "success": True,

                "captured":
                    session["count"],

                "total_photos":
                    session["total_photos"],

                "face_detected":
                    False,

                "complete":
                    False,

                "message":
                    "Face not detected."

            })


        # ----------------------------------------------------
        # LARGEST FACE
        # ----------------------------------------------------

        x, y, w, h = max(

            faces,

            key=lambda rectangle:
                rectangle[2] *
                rectangle[3]

        )


        face_image = gray[
            y:y + h,
            x:x + w
        ]


        if face_image.size == 0:

            return jsonify({

                "success": True,

                "captured":
                    session["count"],

                "total_photos":
                    session["total_photos"],

                "face_detected":
                    False,

                "complete":
                    False

            })


        face_image = cv2.resize(

            face_image,

            (200, 200)

        )


        # ----------------------------------------------------
        # SAVE PHOTO
        # ----------------------------------------------------

        count = (
            session["count"]
            + 1
        )


        filename = (
            f"User.{person_id}."
            f"{count}.jpg"
        )


        file_path = (

            Path(session["folder"])
            / filename

        )


        cv2.imwrite(

            str(file_path),

            face_image

        )


        with registration_lock:

            registration_data[
                person_id
            ]["count"] = count


        complete = (

            count
            >=
            session["total_photos"]

        )


        return jsonify({

            "success": True,

            "captured":
                count,

            "total_photos":
                session["total_photos"],

            "face_detected":
                True,

            "complete":
                complete,

            "x":
                int(x),

            "y":
                int(y),

            "width":
                int(w),

            "height":
                int(h)

        })


    except Exception as error:

        print(
            "Browser frame error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# FINISH STUDENT REGISTRATION
# ============================================================

@browser_camera.route(
    "/api/browser/register/finish",
    methods=["POST"]
)
def browser_register_finish():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "message":
                    "No registration data."

            }), 400


        person_id = int(
            data.get(
                "person_id"
            )
        )


        with registration_lock:

            session = registration_data.get(
                person_id
            )


        if not session:

            return jsonify({

                "success": False,

                "message":
                    "Registration session not found."

            }), 404


        captured = session[
            "count"
        ]

        required = session[
            "total_photos"
        ]


        if captured < 20:

            return jsonify({

                "success": False,

                "message":
                    "At least 20 face photos are required.",

                "captured":
                    captured

            }), 400


        # ----------------------------------------------------
        # SAVE STUDENT
        # ----------------------------------------------------

        students = load_students()

        students[
            str(person_id)
        ] = session["name"]

        save_students(
            students
        )


        # ----------------------------------------------------
        # TRAIN MODEL
        # ----------------------------------------------------

        print()
        print(
            "Training model after browser registration..."
        )

        train_success = train_model()

        # Model file changed after training.
        clear_recognizer_cache()


        if not train_success:

            return jsonify({

                "success": False,

                "message":
                    "Photos captured but model training failed.",

                "captured":
                    captured

            }), 500


        # ----------------------------------------------------
        # REMOVE SESSION
        # ----------------------------------------------------

        with registration_lock:

            registration_data.pop(
                person_id,
                None
            )


        print()
        print(
            "========================================"
        )
        print(
            "BROWSER REGISTRATION COMPLETE"
        )
        print(
            "Student ID:",
            person_id
        )
        print(
            "Name:",
            session["name"]
        )
        print(
            "Photos:",
            captured
        )
        print(
            "========================================"
        )


        return jsonify({

            "success": True,

            "message":
                f"{session['name']} registered successfully with {captured} photos.",

            "id":
                person_id,

            "name":
                session["name"],

            "photos":
                captured

        })


    except Exception as error:

        print(
            "Browser registration finish error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# ============================================================
# NORMALIZE FACE FOR LBPH
# ============================================================

def normalize_face(face):
    try:
        if face is None or face.size == 0:
            return None

        if len(face.shape) == 3:
            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        else:
            gray = face

        gray = cv2.resize(
            gray,
            (200, 200),
            interpolation=cv2.INTER_AREA
        )

        # Same contrast normalization used by the original working code.
        gray = cv2.equalizeHist(gray)

        return gray

    except Exception as error:
        print("Face normalization error:", error)
        return None


# ============================================================
# EMOTION DETECTION
# ============================================================

def detect_emotion(person_id, face_color):
    """
    Detect emotion using the original working DeepFace method.
    Cached briefly because DeepFace is expensive on Render.
    """
    now = time.time()

    with emotion_cache_lock:
        cached = emotion_cache.get(int(person_id))
        if cached and now - cached["time"] < EMOTION_CACHE_SECONDS:
            return cached["emotion"]

    try:
        if face_color is None or face_color.size == 0:
            return "Unknown"

        analysis = DeepFace.analyze(
            face_color,
            actions=["emotion"],
            enforce_detection=False,
            detector_backend="skip",
            align=False
        )

        if isinstance(analysis, list):
            analysis = analysis[0]

        emotion = str(
            analysis.get("dominant_emotion", "Unknown")
        ).capitalize()

        with emotion_cache_lock:
            emotion_cache[int(person_id)] = {
                "emotion": emotion,
                "time": time.time()
            }

        print(
            f"Emotion detected -> ID {int(person_id)}: {emotion}"
        )
        return emotion

    except Exception as error:
        print(
            f"Emotion detection warning for ID {int(person_id)}:",
            error
        )
        return "Unknown"


# ============================================================
# BROWSER FACE RECOGNITION
# ============================================================

@browser_camera.route(
    "/api/browser/process-frame",
    methods=["POST"]
)
def browser_process_frame():

    try:

        frame = decode_image()


        if frame is None:

            return jsonify({

                "success": False,

                "message":
                    "Invalid camera frame."

            }), 400


        students = load_students()


        if not students:

            return jsonify({

                "success": True,

                "recognized":
                    False,

                "message":
                    "No registered students found.",

                "faces": []

            })


        if not CLASSIFIER_FILE.exists():

            return jsonify({

                "success": False,

                "message":
                    "Recognition model not found."

            }), 500


        # ----------------------------------------------------
        # LOAD CACHED LBPH MODEL
        # ----------------------------------------------------

        recognizer = get_cached_recognizer()

        if recognizer is None:
            return jsonify({
                "success": False,
                "message": "Recognition model could not be loaded."
            }), 500


        gray = cv2.cvtColor(

            frame,

            cv2.COLOR_BGR2GRAY

        )


        faces = face_detector.detectMultiScale(

            gray,

            scaleFactor=1.1,

            minNeighbors=6,

            minSize=(80, 80)

        )


        results = []


        for (
            x,
            y,
            w,
            h
        ) in faces:


            face_color = frame[
                y:y + h,
                x:x + w
            ]

            if face_color.size == 0:
                continue

            # Use the original working LBPH normalization.
            face_image = normalize_face(face_color)

            if face_image is None:
                continue


            person_id, confidence = (
                recognizer.predict(
                    face_image
                )
            )


            # ------------------------------------------------
            # LBPH CONFIDENCE
            # Lower value = better match
            # ------------------------------------------------

            recognized = (
                confidence <= 45.0
            )


            person_key = str(
                person_id
            )


            name = students.get(
                person_key,
                "Unknown"
            )


            if not recognized:

                name = "Unknown"


            # ------------------------------------------------
            # EMOTION DETECTION
            # ------------------------------------------------
            # Only run DeepFace for a recognized person. This prevents
            # false/irrelevant emotion work on unknown faces and makes
            # the Render version much faster.
            if recognized:
                emotion = detect_emotion(
                    int(person_id),
                    face_color
                )
            else:
                emotion = "Unknown"

            # ------------------------------------------------
            # MARK ATTENDANCE
            # ------------------------------------------------

            if recognized:
                attendance_marked = mark_attendance(
                    int(person_id),
                    name,
                    emotion
                )
            else:
                attendance_marked = False


            results.append({

                "id":
                    int(person_id),

                "name":
                    name,

                "confidence":
                    round(
                        float(confidence),
                        2
                    ),

                "emotion":
                    emotion,

                "attendance_marked":
                    attendance_marked,

                "x":
                    int(x),

                "y":
                    int(y),

                "width":
                    int(w),

                "height":
                    int(h)

            })


        recognized_person = None


        for result in results:

            if (
                result["name"]
                !=
                "Unknown"
            ):

                recognized_person = result

                break


        return jsonify({

            "success": True,

            "recognized":
                recognized_person is not None,

            "person":
                recognized_person,

            "faces":
                results

        })


    except Exception as error:

        print(
            "Browser recognition error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500
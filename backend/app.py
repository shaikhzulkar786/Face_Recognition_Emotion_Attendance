from flask import Flask, jsonify, send_from_directory, request
from pathlib import Path
from datetime import datetime
import threading
import json
import shutil
import sqlite3

from .attendance import get_attendance


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"

DATASET_DIR = BASE_DIR / "dataset"

DATABASE_DIR = BASE_DIR / "database"

DATABASE_FILE = DATABASE_DIR / "attendance.db"

STUDENTS_FILE = DATABASE_DIR / "students.json"

MODELS_DIR = BASE_DIR / "models"

CLASSIFIER_FILE = MODELS_DIR / "classifier.xml"


DATASET_DIR.mkdir(exist_ok=True)

DATABASE_DIR.mkdir(exist_ok=True)

MODELS_DIR.mkdir(exist_ok=True)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path="/static"
)


# ============================================================
# CAMERA CONTROL
# ============================================================

camera_thread = None

camera_running = False

camera_lock = threading.Lock()


# ============================================================
# STUDENT JSON
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

            data = json.load(file)

        return data

    except Exception as e:

        print(
            "Students JSON error:",
            e
        )

        return {}


# ============================================================
# SAVE STUDENTS
# ============================================================

def save_students(students):

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
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


# ============================================================
# ATTENDANCE API
# ============================================================

@app.route(
    "/api/attendance",
    methods=["GET"]
)
def attendance_api():

    try:

        records = get_attendance()

        result = []

        for record in records:

            result.append({

                "id": record[0],

                "person_id": record[1],

                "name": record[2],

                "emotion": record[3],

                "date": record[4],

                "time": record[5]

            })

        return jsonify(result)

    except Exception as e:

        print(
            "Attendance API error:",
            e
        )

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# ============================================================
# DELETE ATTENDANCE RECORD
# ============================================================

@app.route(
    "/api/attendance/<int:attendance_id>",
    methods=["DELETE"]
)
def delete_attendance_record(attendance_id):

    try:

        connection = sqlite3.connect(
            DATABASE_FILE
        )

        cursor = connection.cursor()


        # ----------------------------------------------------
        # FIND ATTENDANCE RECORD
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT id, person_id, name, emotion, date, time
            FROM attendance
            WHERE id = ?
            """,
            (attendance_id,)
        )

        record = cursor.fetchone()


        # ----------------------------------------------------
        # RECORD NOT FOUND
        # ----------------------------------------------------

        if not record:

            connection.close()

            return jsonify({

                "success": False,

                "message":
                    f"Attendance record {attendance_id} not found."

            }), 404


        # ----------------------------------------------------
        # DELETE ONLY THIS ATTENDANCE RECORD
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM attendance
            WHERE id = ?
            """,
            (attendance_id,)
        )

        deleted_rows = cursor.rowcount


        connection.commit()

        connection.close()


        # ----------------------------------------------------
        # CHECK DELETE
        # ----------------------------------------------------

        if deleted_rows == 0:

            return jsonify({

                "success": False,

                "message":
                    "Attendance record could not be deleted."

            }), 500


        print(
            f"Attendance record {attendance_id} "
            f"({record[2]}) deleted successfully."
        )


        return jsonify({

            "success": True,

            "message":
                f"Attendance record {attendance_id} "
                f"deleted successfully."

        })


    except Exception as e:

        print(
            "DELETE ATTENDANCE ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# ============================================================
# STATS API
# ============================================================

@app.route(
    "/api/stats",
    methods=["GET"]
)
def stats_api():

    try:

        connection = sqlite3.connect(
            DATABASE_FILE
        )

        cursor = connection.cursor()


        # ----------------------------------------------------
        # TOTAL RECORDS
        # ----------------------------------------------------

        cursor.execute(
            "SELECT COUNT(*) FROM attendance"
        )

        total_records = cursor.fetchone()[0]


        # ----------------------------------------------------
        # TODAY'S ATTENDANCE
        # ----------------------------------------------------

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )


        cursor.execute(
            """
            SELECT COUNT(*)
            FROM attendance
            WHERE date = ?
            """,
            (today,)
        )

        today_attendance = cursor.fetchone()[0]


        connection.close()


        # ----------------------------------------------------
        # REGISTERED STUDENTS
        # ----------------------------------------------------

        students = load_students()

        registered_students = len(students)


        return jsonify({

            "total_records":
                total_records,

            "today_attendance":
                today_attendance,

            "registered_students":
                registered_students

        })


    except Exception as e:

        print(
            "Stats error:",
            e
        )

        return jsonify({

            "total_records": 0,

            "today_attendance": 0,

            "registered_students": 0

        })


# ============================================================
# REGISTERED STUDENTS API
# ============================================================

@app.route(
    "/api/students",
    methods=["GET"]
)
def students_api():

    try:

        students = load_students()

        result = []


        for student_id, name in students.items():

            folder = DATASET_DIR / str(
                student_id
            )

            photo_count = 0


            if folder.exists():

                photo_count = len([

                    file

                    for file in folder.iterdir()

                    if file.is_file()

                    and file.suffix.lower()

                    in [
                        ".jpg",
                        ".jpeg",
                        ".png"
                    ]

                ])


            result.append({

                "id":
                    int(student_id),

                "name":
                    name,

                "photos":
                    photo_count,

                "status":
                    "Registered"

            })


        result.sort(
            key=lambda x: x["id"]
        )


        return jsonify(result)


    except Exception as e:

        print(
            "Students API error:",
            e
        )

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# ============================================================
# REGISTER NEW STUDENT
# ============================================================

@app.route(
    "/api/register",
    methods=["POST"]
)
def register_student():

    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "success": False,

                "message":
                    "No registration data received."

            }), 400


        person_id = int(
            data.get("person_id")
        )


        name = str(
            data.get("name", "")
        ).strip()


        photos = int(
            data.get(
                "photos",
                200
            )
        )


        # ----------------------------------------------------
        # VALIDATE STUDENT ID
        # ----------------------------------------------------

        if person_id <= 0:

            return jsonify({

                "success": False,

                "message":
                    "Student ID must be greater than 0."

            }), 400


        # ----------------------------------------------------
        # VALIDATE NAME
        # ----------------------------------------------------

        if not name:

            return jsonify({

                "success": False,

                "message":
                    "Student name is required."

            }), 400


        # ----------------------------------------------------
        # VALIDATE PHOTO COUNT
        # ----------------------------------------------------

        if photos <= 0:

            return jsonify({

                "success": False,

                "message":
                    "Photo count must be greater than 0."

            }), 400


        print(
            "\n========================================"
        )

        print(
            "STUDENT REGISTRATION"
        )

        print(
            "========================================"
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
            photos
        )


        # ====================================================
        # IMPORT FUNCTIONS
        # ====================================================

        from .capture_faces import capture_faces

        from .train import train_model


        # ====================================================
        # SAVE STUDENT NAME
        # ====================================================

        students = load_students()

        students[str(person_id)] = name

        save_students(students)


        # ====================================================
        # CAPTURE PHOTOS
        # ====================================================

        capture_success = capture_faces(
            person_id,
            name,
            total_photos=photos
        )


        if not capture_success:

            return jsonify({

                "success": False,

                "message":
                    "Photo capture failed."

            }), 500


        # ====================================================
        # TRAIN MODEL
        # ====================================================

        print(
            "Training recognition model..."
        )


        train_success = train_model()


        if not train_success:

            return jsonify({

                "success": False,

                "message":
                    "Photos captured, but model training failed."

            }), 500


        print(
            "Student registered successfully."
        )


        print(
            "========================================\n"
        )


        return jsonify({

            "success": True,

            "message":
                f"Student {name} registered successfully. "
                f"{photos} photos captured and model trained."

        })


    except Exception as e:

        print(
            "\nREGISTRATION ERROR:"
        )

        print(
            repr(e)
        )


        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# ============================================================
# DELETE STUDENT
# ============================================================

@app.route(
    "/api/students/<int:student_id>",
    methods=["DELETE"]
)
def delete_student(student_id):

    try:

        print(
            "\n========================================"
        )

        print(
            "DELETE STUDENT"
        )

        print(
            "Student ID:",
            student_id
        )


        students = load_students()

        student_key = str(
            student_id
        )


        # ====================================================
        # CHECK STUDENT
        # ====================================================

        if student_key not in students:

            print(
                "Student not found."
            )


            return jsonify({

                "success": False,

                "message":
                    f"Student ID {student_id} not found."

            }), 404


        student_name = students[
            student_key
        ]


        # ====================================================
        # DELETE DATASET
        # ====================================================

        student_folder = (
            DATASET_DIR /
            student_key
        )


        if student_folder.exists():

            shutil.rmtree(
                student_folder
            )

            print(
                "Dataset deleted."
            )


        # ====================================================
        # DELETE STUDENT FROM JSON
        # ====================================================

        del students[
            student_key
        ]


        save_students(
            students
        )


        print(
            "Student removed from students.json."
        )


        # ====================================================
        # DELETE ATTENDANCE RECORDS
        # ====================================================

        connection = sqlite3.connect(
            DATABASE_FILE
        )

        cursor = connection.cursor()


        cursor.execute(
            """
            DELETE FROM attendance
            WHERE person_id = ?
            """,
            (student_id,)
        )


        deleted_attendance = cursor.rowcount


        connection.commit()

        connection.close()


        print(
            "Attendance records deleted:",
            deleted_attendance
        )


        # ====================================================
        # RETRAIN MODEL
        # ====================================================

        try:

            from .train import train_model


            train_result = train_model()


            print(
                "Model retraining:",
                train_result
            )


        except Exception as train_error:

            print(
                "Model retraining warning:",
                train_error
            )


        print(
            f"Student ID {student_id} "
            f"({student_name}) deleted successfully."
        )


        print(
            "========================================\n"
        )


        return jsonify({

            "success": True,

            "message":
                f"Student ID {student_id} "
                f"({student_name}) deleted successfully."

        })


    except Exception as e:

        print(
            "\nDELETE ERROR:"
        )

        print(
            repr(e)
        )


        return jsonify({

            "success": False,

            "message":
                str(e)

        }), 500


# ============================================================
# CAMERA START
# ============================================================

@app.route(
    "/api/start-camera",
    methods=["POST"]
)
def start_camera():

    global camera_thread

    global camera_running


    try:

        with camera_lock:

            if camera_running:

                return jsonify({

                    "success": True,

                    "message":
                        "Camera is already running."

                })


            camera_running = True


        def run_camera():

            global camera_running


            try:

                from .main import main

                main()


            except Exception as e:

                print(
                    "Camera error:",
                    e
                )


            finally:

                with camera_lock:

                    camera_running = False


        camera_thread = threading.Thread(
            target=run_camera,
            daemon=True
        )


        camera_thread.start()


        return jsonify({

            "success": True,

            "message":
                "Camera started."

        })


    except Exception as e:

        camera_running = False


        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# ============================================================
# CAMERA STOP
# ============================================================

@app.route(
    "/api/stop-camera",
    methods=["POST"]
)
def stop_camera():

    global camera_running


    try:

        camera_running = False


        return jsonify({

            "success": True,

            "message":
                "Camera stop requested."

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# ============================================================
# CAMERA STATUS
# ============================================================

@app.route(
    "/api/camera-status",
    methods=["GET"]
)
def camera_status():

    return jsonify({

        "running":
            camera_running

    })


# ============================================================
# RUN FLASK
# ============================================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "SMART ATTENDANCE SYSTEM"
    )

    print(
        "========================================"
    )

    print(
        "Website:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print(
        "========================================"
    )


    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )
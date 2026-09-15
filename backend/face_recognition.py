import cv2

from .emotion_detection import detect_emotion
from .attendance import mark_attendance

from .config import (
    FACE_CASCADE,
    CLASSIFIER_FILE,
    SCALE_FACTOR,
    MIN_NEIGHBORS,
    RECOGNITION_THRESHOLD,
    NAMES
)


class FaceRecognizer:

    def __init__(self):

        self.face_cascade = cv2.CascadeClassifier(
            FACE_CASCADE
        )

        if self.face_cascade.empty():
            raise FileNotFoundError(
                f"Face cascade not loaded: {FACE_CASCADE}"
            )

        self.classifier = (
            cv2.face.LBPHFaceRecognizer_create()
        )

        self.classifier.read(
            CLASSIFIER_FILE
        )

    # ====================================================
    # RECOGNIZE FIRST FACE ONLY
    # ====================================================

    def recognize(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=SCALE_FACTOR,
            minNeighbors=MIN_NEIGHBORS,
            minSize=(80, 80)
        )

        results = []

        # ------------------------------------------------
        # NO FACE
        # ------------------------------------------------

        if len(faces) == 0:
            return frame, results

        # ------------------------------------------------
        # ONLY FIRST DETECTED FACE
        # ------------------------------------------------

        x, y, w, h = faces[0]

        face = gray[
            y:y + h,
            x:x + w
        ]

        if face.size == 0:
            return frame, results

        face = cv2.resize(
            face,
            (200, 200)
        )

        # ------------------------------------------------
        # RECOGNITION
        # ------------------------------------------------

        person_id, prediction = (
            self.classifier.predict(face)
        )

        print(
            "Predicted ID:",
            person_id,
            "Distance:",
            prediction
        )

        # ------------------------------------------------
        # CONFIDENCE
        # ------------------------------------------------

        confidence = int(
            max(
                0,
                min(
                    100,
                    100 * (
                        1 - prediction / 300
                    )
                )
            )
        )

        # ------------------------------------------------
        # NAME
        # ------------------------------------------------

        if confidence >= RECOGNITION_THRESHOLD:

            name = NAMES.get(
                person_id,
                "Unknown"
            )

        else:

            name = "Unknown"

        # ------------------------------------------------
        # EMOTION
        # ------------------------------------------------

        emotion = "Unknown"

        try:

            face_color = frame[
                y:y + h,
                x:x + w
            ]

            if face_color.size > 0:

                emotion = detect_emotion(
                    face_color
                )

        except Exception as e:

            print(
                "Emotion error:",
                e
            )

        # ------------------------------------------------
        # ATTENDANCE
        # ------------------------------------------------

        if name != "Unknown":

            marked = mark_attendance(
                int(person_id),
                name,
                emotion
            )

            print(
                f"First recognized student: {name}"
            )

        # ------------------------------------------------
        # COLOR
        # ------------------------------------------------

        if name == "Unknown":

            color = (0, 0, 255)

        else:

            color = (0, 255, 0)

        # ------------------------------------------------
        # FACE BOX
        # ------------------------------------------------

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            color,
            2
        )

        # ------------------------------------------------
        # NAME + EMOTION
        # ------------------------------------------------

        label = (
            f"{name} - {emotion}"
        )

        cv2.putText(
            frame,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
            cv2.LINE_AA
        )

        # ------------------------------------------------
        # CONFIDENCE
        # ------------------------------------------------

        cv2.putText(
            frame,
            f"Confidence: {confidence}%",
            (x, y + h + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            1,
            cv2.LINE_AA
        )

        # ------------------------------------------------
        # RESULT
        # ------------------------------------------------

        results.append({

            "id": int(person_id),

            "name": name,

            "confidence": confidence,

            "emotion": emotion,

            "box": [x, y, w, h]
        })

        return frame, results
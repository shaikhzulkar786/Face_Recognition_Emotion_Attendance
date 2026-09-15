import cv2

from .config import CAMERA_INDEX
from .face_recognition import FaceRecognizer


def main():

    recognizer = FaceRecognizer()

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )

    if not camera.isOpened():

        print(
            "ERROR: Camera open nahi ho raha."
        )

        return

    # ====================================================
    # CAMERA RESOLUTION
    # ====================================================

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        640
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        480
    )

    camera.set(
        cv2.CAP_PROP_BUFFERSIZE,
        1
    )

    print()
    print("=" * 60)
    print("LIVE ATTENDANCE CAMERA")
    print("=" * 60)
    print(
        "Pehla recognized student = attendance"
    )
    print(
        "Attendance ke baad camera automatically OFF hoga."
    )
    print("=" * 60)

    # ====================================================
    # CAMERA LOOP
    # ====================================================

    while True:

        ret, frame = camera.read()

        if not ret:

            print(
                "ERROR: Camera se frame nahi mila."
            )

            break

        # ------------------------------------------------
        # RECOGNIZE
        # ------------------------------------------------

        frame, results = (
            recognizer.recognize(frame)
        )

        # ------------------------------------------------
        # SHOW
        # ------------------------------------------------

        cv2.imshow(
            "Face Recognition + Emotion Detection",
            frame
        )

        # ------------------------------------------------
        # FIRST RECOGNIZED STUDENT
        # ------------------------------------------------

        if results:

            first_result = results[0]

            if (
                first_result["name"]
                != "Unknown"
            ):

                print()
                print(
                    "=" * 60
                )

                print(
                    "FIRST STUDENT DETECTED"
                )

                print(
                    "ID:",
                    first_result["id"]
                )

                print(
                    "Name:",
                    first_result["name"]
                )

                print(
                    "Emotion:",
                    first_result["emotion"]
                )

                print(
                    "Attendance marked."
                )

                print(
                    "Camera automatically stopping..."
                )

                print(
                    "=" * 60
                )

                # ----------------------------------------
                # CAMERA STOP
                # ----------------------------------------

                break

        # ------------------------------------------------
        # ENTER = MANUAL STOP
        # ------------------------------------------------

        key = cv2.waitKey(1) & 0xFF

        if key == 13:

            print(
                "Camera manually stopped."
            )

            break

    # ====================================================
    # RELEASE
    # ====================================================

    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":

    main()
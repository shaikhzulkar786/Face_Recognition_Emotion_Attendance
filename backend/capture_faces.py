import cv2
import os
import time

from .config import DATASET_DIR, FACE_CASCADE


def capture_faces(person_id, name, total_photos=200):

    print()
    print("=" * 60)
    print("SMART ATTENDANCE - FACE CAPTURE")
    print("=" * 60)

    person_id = int(person_id)
    total_photos = int(total_photos)

    # --------------------------------------------------
    # STUDENT FOLDER
    # --------------------------------------------------

    student_folder = os.path.join(
        DATASET_DIR,
        str(person_id)
    )

    os.makedirs(student_folder, exist_ok=True)

    # --------------------------------------------------
    # REMOVE OLD PHOTOS OF THIS ID ONLY
    # --------------------------------------------------

    deleted = 0

    for filename in os.listdir(student_folder):

        if filename.lower().endswith(
            (".jpg", ".jpeg", ".png")
        ):

            file_path = os.path.join(
                student_folder,
                filename
            )

            try:
                os.remove(file_path)
                deleted += 1
            except Exception as e:
                print("Old photo delete error:", e)

    print(f"Old photos removed: {deleted}")
    print(f"Student: {name}")
    print(f"ID: {person_id}")
    print(f"Target photos: {total_photos}")

    # --------------------------------------------------
    # FACE CASCADE
    # --------------------------------------------------

    face_cascade = cv2.CascadeClassifier(
        FACE_CASCADE
    )

    if face_cascade.empty():

        print("ERROR: Haarcascade load nahi hua.")
        return False

    # --------------------------------------------------
    # CAMERA
    # --------------------------------------------------

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Camera open nahi ho raha.")
        return False

    # Camera resolution
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print()
    print("Camera started.")
    print("Sirf ek face camera ke saamne rakho.")
    print("Photos automatically capture hongi.")
    print("200 photos ke baad camera automatically OFF hoga.")
    print()

    count = 0

    # Small delay before starting
    time.sleep(2)

    # --------------------------------------------------
    # CAPTURE LOOP
    # --------------------------------------------------

    while count < total_photos:

        ret, frame = camera.read()

        if not ret:

            print("ERROR: Camera frame nahi mila.")
            break

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=8,
            minSize=(100, 100)
        )

        # --------------------------------------------------
        # ONLY ONE FACE ALLOWED
        # --------------------------------------------------

        if len(faces) == 1:

            x, y, w, h = faces[0]

            # Face crop
            face = gray[
                y:y + h,
                x:x + w
            ]

            # Resize face
            face = cv2.resize(
                face,
                (200, 200)
            )

            count += 1

            filename = os.path.join(
                student_folder,
                f"User.{person_id}.{count}.jpg"
            )

            cv2.imwrite(
                filename,
                face
            )

            # Draw rectangle
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Captured: {count}/{total_photos}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            print(
                f"Photo captured: {count}/{total_photos}"
            )

        elif len(faces) == 0:

            cv2.putText(
                frame,
                "Face not detected",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                2
            )

        else:

            cv2.putText(
                frame,
                "ONLY ONE FACE ALLOWED",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                2
            )

        # --------------------------------------------------
        # SHOW CAMERA
        # --------------------------------------------------

        cv2.imshow(
            "Register Student - Face Capture",
            frame
        )

        # Emergency exit
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            print("Capture cancelled by user.")
            camera.release()
            cv2.destroyAllWindows()
            return False

    # --------------------------------------------------
    # AUTOMATIC CAMERA OFF
    # --------------------------------------------------

    camera.release()
    cv2.destroyAllWindows()

    print()
    print("=" * 60)
    print(f"Student : {name}")
    print(f"Person ID : {person_id}")
    print(f"{count} photos captured.")
    print("Camera automatically stopped.")
    print("=" * 60)

    # --------------------------------------------------
    # CHECK
    # --------------------------------------------------

    if count < total_photos:

        print("ERROR: Required photos complete nahi hui.")
        return False

    return True


if __name__ == "__main__":

    capture_faces(
        person_id=1,
        name="Zulkar Nain",
        total_photos=200
    )
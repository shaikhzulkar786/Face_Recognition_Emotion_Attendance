import cv2
import os

from .config import DATASET_DIR


def capture_faces(person_id):
    os.makedirs(DATASET_DIR, exist_ok=True)

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Camera open nahi ho raha!")
        return

    count = 0

    print("Camera started.")
    print("Face camera ke saamne rakho.")
    print("Images capture ho rahi hain...")
    print("Q press karke band karo.")

    while True:
        ret, frame = camera.read()

        if not ret:
            print("Camera se frame nahi mila.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )

        for (x, y, w, h) in faces:
            count += 1

            face = gray[y:y + h, x:x + w]

            filename = os.path.join(
                DATASET_DIR,
                f"User.{person_id}.{count}.jpg"
            )

            cv2.imwrite(filename, face)

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Images: {count}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        cv2.imshow("Dataset Capture", frame)

        if cv2.waitKey(100) & 0xFF == ord("q"):
            break

        if count >= 300:
            print("30 images captured.")
            break

    camera.release()
    cv2.destroyAllWindows()

    print(f"Dataset saved in: {DATASET_DIR}")


if __name__ == "__main__":
    person_id = int(input("Person ID enter karo: "))
    capture_faces(person_id)
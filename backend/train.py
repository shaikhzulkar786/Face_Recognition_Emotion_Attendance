import cv2
import os
import numpy as np

from .config import (
    DATASET_DIR,
    CLASSIFIER_FILE,
    FACE_CASCADE
)


# ============================================================
# TRAIN FACE RECOGNITION MODEL
# ============================================================

def train_model():

    print("\n========================================")
    print("TRAINING FACE RECOGNITION MODEL")
    print("========================================")

    try:

        # ====================================================
        # LOAD HAAR CASCADE
        # ====================================================

        face_cascade = cv2.CascadeClassifier(
            FACE_CASCADE
        )

        if face_cascade.empty():

            print(
                "ERROR: Haar Cascade load nahi hua."
            )

            return False


        # ====================================================
        # CREATE LBPH RECOGNIZER
        # ====================================================

        recognizer = cv2.face.LBPHFaceRecognizer_create()


        faces = []
        ids = []


        # ====================================================
        # CHECK DATASET
        # ====================================================

        if not os.path.exists(DATASET_DIR):

            print(
                "ERROR: Dataset folder nahi mila."
            )

            return False


        # ====================================================
        # GET STUDENT FOLDERS
        # ====================================================

        student_folders = [

            folder

            for folder in os.listdir(
                DATASET_DIR
            )

            if os.path.isdir(
                os.path.join(
                    DATASET_DIR,
                    folder
                )
            )

            and folder.isdigit()

        ]


        if not student_folders:

            print(
                "ERROR: Dataset me koi student nahi hai."
            )

            return False


        # ====================================================
        # READ EACH STUDENT DATASET
        # ====================================================

        for student_id in sorted(
            student_folders,
            key=int
        ):

            student_path = os.path.join(
                DATASET_DIR,
                student_id
            )


            print(
                f"\nStudent ID: {student_id}"
            )


            # =================================================
            # GET IMAGES
            # =================================================

            image_files = [

                file

                for file in os.listdir(
                    student_path
                )

                if file.lower().endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png"
                    )
                )

            ]


            count = 0


            # =================================================
            # READ IMAGES
            # =================================================

            for image_file in image_files:

                image_path = os.path.join(
                    student_path,
                    image_file
                )


                image = cv2.imread(
                    image_path,
                    cv2.IMREAD_GRAYSCALE
                )


                if image is None:

                    print(
                        "Image read failed:",
                        image_file
                    )

                    continue


                # =============================================
                # FACE DETECTION
                # =============================================

                detected_faces = face_cascade.detectMultiScale(
                    image,
                    scaleFactor=1.1,
                    minNeighbors=5
                )


                # =============================================
                # FACE FOUND
                # =============================================

                if len(detected_faces) > 0:

                    for (
                        x,
                        y,
                        w,
                        h
                    ) in detected_faces:

                        face = image[
                            y:y + h,
                            x:x + w
                        ]


                        if face.size == 0:

                            continue


                        faces.append(
                            face
                        )

                        ids.append(
                            int(student_id)
                        )

                        count += 1


                # =============================================
                # FACE NOT FOUND
                # =============================================

                else:

                    # Dataset images are already
                    # cropped face images.

                    if image.size > 0:

                        faces.append(
                            image
                        )

                        ids.append(
                            int(student_id)
                        )

                        count += 1


            print(
                f"Images used: {count}"
            )


        # ====================================================
        # CHECK TRAINING DATA
        # ====================================================

        if len(faces) == 0:

            print(
                "ERROR: Training ke liye koi face data nahi mila."
            )

            return False


        print(
            "\nTotal training images:",
            len(faces)
        )


        # ====================================================
        # TRAIN MODEL
        # ====================================================

        print(
            "\nTraining model..."
        )


        recognizer.train(
            faces,
            np.array(ids)
        )


        # ====================================================
        # CREATE MODELS FOLDER
        # ====================================================

        model_folder = os.path.dirname(
            CLASSIFIER_FILE
        )


        if model_folder:

            os.makedirs(
                model_folder,
                exist_ok=True
            )


        # ====================================================
        # SAVE CLASSIFIER
        # ====================================================

        recognizer.write(
            CLASSIFIER_FILE
        )


        # ====================================================
        # SUCCESS
        # ====================================================

        print(
            "\n========================================"
        )

        print(
            "MODEL SUCCESSFULLY TRAINED"
        )

        print(
            "========================================"
        )

        print(
            "Model:",
            CLASSIFIER_FILE
        )

        print(
            "Total images:",
            len(faces)
        )

        print(
            "Student IDs:",
            sorted(set(ids))
        )

        print(
            "========================================\n"
        )


        return True


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        print(
            "\n========================================"
        )

        print(
            "TRAINING ERROR"
        )

        print(
            "========================================"
        )

        print(
            repr(e)
        )

        print(
            "========================================\n"
        )

        return False


# ============================================================
# DIRECT RUN
# ============================================================

if __name__ == "__main__":

    success = train_model()

    if success:

        print(
            "Training complete."
        )

    else:

        print(
            "Training failed."
        )
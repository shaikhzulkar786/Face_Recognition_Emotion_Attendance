import cv2
import os
import numpy as np

from .config import (
    DATASET_DIR,
    CLASSIFIER_FILE
)


# ============================================================
# NORMALIZE FACE
# ============================================================

def normalize_face(image):

    try:

        if image is None:
            return None

        # Convert to grayscale if needed
        if len(image.shape) == 3:

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

        else:

            gray = image


        # Same size as live recognition
        gray = cv2.resize(
            gray,
            (200, 200),
            interpolation=cv2.INTER_AREA
        )


        # Same contrast processing as recognition
        gray = cv2.equalizeHist(
            gray
        )


        return gray


    except Exception as e:

        print(
            "Face normalization error:",
            e
        )

        return None


# ============================================================
# TRAIN FACE RECOGNITION MODEL
# ============================================================

def train_model():

    print()
    print("========================================")
    print("     TRAINING FACE RECOGNITION MODEL")
    print("========================================")


    try:

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
        # CREATE LBPH
        # ====================================================

        recognizer = (
            cv2.face.LBPHFaceRecognizer_create(
                radius=1,
                neighbors=8,
                grid_x=8,
                grid_y=8
            )
        )


        faces = []
        ids = []


        # ====================================================
        # READ ALL STUDENT DATA
        # ====================================================

        for student_id in sorted(
            student_folders,
            key=int
        ):

            student_path = os.path.join(
                DATASET_DIR,
                student_id
            )


            print()
            print(
                f"Student ID: {student_id}"
            )


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
            # READ EACH IMAGE
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
                # IMPORTANT
                # =============================================
                #
                # Browser registration already saves
                # cropped face images.
                #
                # Therefore DO NOT run Haar detection again.
                #
                # Use exactly the same normalization as
                # live recognition.
                # =============================================

                face = normalize_face(
                    image
                )


                if face is None:

                    continue


                if face.size == 0:

                    continue


                faces.append(
                    face
                )


                ids.append(
                    int(student_id)
                )


                count += 1


            print(
                f"Images used: {count}"
            )


        # ====================================================
        # CHECK DATA
        # ====================================================

        if len(faces) == 0:

            print()
            print(
                "ERROR: Training ke liye koi image nahi mili."
            )

            return False


        print()
        print(
            "Total training images:",
            len(faces)
        )


        print()
        print(
            "Training model..."
        )


        # ====================================================
        # TRAIN
        # ====================================================

        recognizer.train(
            faces,
            np.array(ids)
        )


        # ====================================================
        # CREATE MODEL DIRECTORY
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
        # SAVE MODEL
        # ====================================================

        recognizer.write(
            CLASSIFIER_FILE
        )


        # ====================================================
        # SUCCESS
        # ====================================================

        print()
        print("========================================")
        print("      MODEL SUCCESSFULLY TRAINED")
        print("========================================")


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


        print("========================================")
        print()


        return True


    except Exception as e:

        print()
        print("========================================")
        print("          TRAINING ERROR")
        print("========================================")


        print(
            repr(e)
        )


        print("========================================")
        print()


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
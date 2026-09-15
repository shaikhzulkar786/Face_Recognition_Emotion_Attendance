import os
import json


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# PATHS
# ============================================================

FACE_CASCADE = os.path.join(
    BASE_DIR,
    "models",
    "haarcascade_frontalface_default.xml"
)

CLASSIFIER_FILE = os.path.join(
    BASE_DIR,
    "models",
    "classifier.xml"
)

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset"
)

DATABASE_DIR = os.path.join(
    BASE_DIR,
    "database"
)

DATABASE_FILE = os.path.join(
    DATABASE_DIR,
    "attendance.db"
)

STUDENTS_FILE = os.path.join(
    DATABASE_DIR,
    "students.json"
)


# ============================================================
# CAMERA SETTINGS
# ============================================================

CAMERA_INDEX = 0

SCALE_FACTOR = 1.1

MIN_NEIGHBORS = 10

RECOGNITION_THRESHOLD = 78


# ============================================================
# STUDENT DATABASE
# ============================================================

def load_students():

    """
    students.json se saare students load karta hai.

    Example:

    {
        "1": "Zulkar Nain",
        "2": "Zulfikar",
        "3": "Aakil",
        "4": "Saidur"
    }
    """

    try:

        # Database folder automatically create
        os.makedirs(
            DATABASE_DIR,
            exist_ok=True
        )

        # Agar students.json nahi hai
        if not os.path.exists(STUDENTS_FILE):

            with open(
                STUDENTS_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    {},
                    file,
                    indent=4
                )

            return {}

        # JSON read
        with open(
            STUDENTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        students = {}

        # Convert ID string → integer
        for student_id, name in data.items():

            try:

                students[int(student_id)] = str(name)

            except ValueError:

                print(
                    f"Invalid student ID ignored: {student_id}"
                )

        return students

    except Exception as e:

        print(
            "Students JSON loading error:",
            e
        )

        return {}


# ============================================================
# SAVE STUDENT
# ============================================================

def save_student(student_id, name):

    """
    New student ko students.json me automatically save karta hai.

    Code me naam manually add karne ki zarurat nahi.
    """

    try:

        student_id = int(student_id)

        name = str(name).strip()

        if student_id <= 0:

            raise ValueError(
                "Student ID must be greater than 0."
            )

        if not name:

            raise ValueError(
                "Student name cannot be empty."
            )

        os.makedirs(
            DATABASE_DIR,
            exist_ok=True
        )

        # Existing students
        students = load_students()

        # New / updated student
        students[student_id] = name

        # Sorted JSON
        data = {

            str(student_id): students[student_id]

            for student_id in sorted(
                students.keys()
            )

        }

        # Save
        with open(
            STUDENTS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        print()
        print(
            f"Student saved: {student_id} -> {name}"
        )

        return True

    except Exception as e:

        print(
            "Student save error:",
            e
        )

        return False


# ============================================================
# DELETE STUDENT
# ============================================================

def delete_student(student_id):

    """
    students.json se student delete karta hai.
    """

    try:

        student_id = int(student_id)

        students = load_students()

        if student_id not in students:

            print(
                f"Student ID {student_id} not found."
            )

            return False

        del students[student_id]

        data = {

            str(student_id): students[student_id]

            for student_id in sorted(
                students.keys()
            )

        }

        with open(
            STUDENTS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"Student deleted: {student_id}"
        )

        return True

    except Exception as e:

        print(
            "Student delete error:",
            e
        )

        return False


# ============================================================
# GET STUDENT NAME
# ============================================================

def get_student_name(student_id):

    """
    Student ID se naam return karta hai.
    """

    students = load_students()

    return students.get(
        int(student_id),
        "Unknown"
    )


# ============================================================
# DYNAMIC NAMES
# ============================================================

# Startup par students load honge.
# Face recognition ke time latest students.json
# dobara load karna better hai.

NAMES = load_students()
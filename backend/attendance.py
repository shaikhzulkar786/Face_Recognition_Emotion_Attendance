import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


# =========================================================
# DATABASE PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_FILE = DATABASE_DIR / "attendance.db"


# =========================================================
# INDIA TIMEZONE
# =========================================================

INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")


def get_india_time():
    """
    Always return current India time (IST),
    regardless of server timezone.
    """
    return datetime.now(INDIA_TIMEZONE)


# =========================================================
# OLD STUDENTS
# =========================================================
# Sirf existing old students ke liye.
# Future students yahan add nahi karne hain.
# =========================================================

OLD_STUDENTS = {
    1: "Zulkar Nain",
    2: "Zulfikar",
    3: "Aakil"
}


# =========================================================
# CREATE DATABASE
# =========================================================

def create_database():

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    # -----------------------------------------------------
    # ATTENDANCE TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER,
            name TEXT NOT NULL,
            emotion TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # STUDENTS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            person_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            registered_at TEXT NOT NULL
        )
    """)

    # =====================================================
    # FIX OLD STUDENT NAMES
    # =====================================================

    for person_id, name in OLD_STUDENTS.items():

        cursor.execute("""
            SELECT name
            FROM students
            WHERE person_id = ?
        """, (person_id,))

        existing = cursor.fetchone()

        # Student doesn't exist
        if existing is None:

            cursor.execute("""
                INSERT INTO students
                (
                    person_id,
                    name,
                    registered_at
                )
                VALUES (?, ?, ?)
            """, (
                person_id,
                name,
                get_india_time().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ))

        # Existing generic name ko correct karo
        elif existing[0].startswith("Student "):

            cursor.execute("""
                UPDATE students
                SET name = ?
                WHERE person_id = ?
            """, (
                name,
                person_id
            ))

    connection.commit()
    connection.close()


# =========================================================
# REGISTER / UPDATE STUDENT
# =========================================================

def register_student(person_id, name):

    create_database()

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    registered_at = get_india_time().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO students
        (
            person_id,
            name,
            registered_at
        )
        VALUES (?, ?, ?)

        ON CONFLICT(person_id)
        DO UPDATE SET
            name = excluded.name,
            registered_at = excluded.registered_at
    """, (
        person_id,
        name,
        registered_at
    ))

    connection.commit()
    connection.close()

    print(
        f"Student saved: {person_id} | {name}"
    )


# =========================================================
# GET STUDENT NAME
# =========================================================

def get_student_name(person_id):

    create_database()

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM students
        WHERE person_id = ?
    """, (person_id,))

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]

    return "Unknown"


# =========================================================
# GET ALL STUDENTS
# =========================================================

def get_students():

    create_database()

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            person_id,
            name,
            registered_at
        FROM students
        ORDER BY person_id
    """)

    records = cursor.fetchall()

    connection.close()

    return records


# =========================================================
# DELETE STUDENT
# =========================================================

def delete_student(person_id):

    create_database()

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM students
        WHERE person_id = ?
    """, (person_id,))

    connection.commit()

    deleted = cursor.rowcount > 0

    connection.close()

    return deleted


# =========================================================
# MARK ATTENDANCE
# =========================================================

def mark_attendance(
    person_id,
    name,
    emotion="Unknown"
):

    try:

        create_database()

        # -------------------------------------------------
        # INDIA TIME
        # -------------------------------------------------

        now = get_india_time()

        date = now.strftime(
            "%Y-%m-%d"
        )

        time = now.strftime(
            "%H:%M:%S"
        )

        connection = sqlite3.connect(
            DATABASE_FILE
        )

        cursor = connection.cursor()

        # -------------------------------------------------
        # CHECK TODAY'S ATTENDANCE
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM attendance
            WHERE person_id = ?
            AND date = ?
        """, (
            person_id,
            date
        ))

        existing_record = cursor.fetchone()

        if existing_record:

            connection.close()

            print(
                f"Attendance already marked: {name}"
            )

            return False

        # -------------------------------------------------
        # INSERT ATTENDANCE
        # -------------------------------------------------

        cursor.execute("""
            INSERT INTO attendance
            (
                person_id,
                name,
                emotion,
                date,
                time
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            person_id,
            name,
            emotion,
            date,
            time
        ))

        connection.commit()
        connection.close()

        print(
            f"Attendance marked: "
            f"{name} | "
            f"{emotion} | "
            f"{date} {time} IST"
        )

        return True

    except Exception as e:

        print(
            "Attendance error:",
            e
        )

        return False


# =========================================================
# GET ATTENDANCE
# =========================================================

def get_attendance():

    create_database()

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            person_id,
            name,
            emotion,
            date,
            time
        FROM attendance
        ORDER BY
            date DESC,
            time DESC
    """)

    records = cursor.fetchall()

    connection.close()

    return records
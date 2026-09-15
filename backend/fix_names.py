import sqlite3
from pathlib import Path
import re


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_FILE = BASE_DIR / "database" / "attendance.db"
CONFIG_FILE = BASE_DIR / "backend" / "config.py"


# =========================================================
# STUDENT NAMES
# =========================================================

STUDENT_NAMES = {
    1: "Zulkar Nain",
    2: "Zulfikar",
    3: "Aakil"
}


# =========================================================
# FIX DATABASE NAMES
# =========================================================

def fix_database_names():

    if not DATABASE_FILE.exists():
        print("ERROR: Database file nahi mila.")
        print(DATABASE_FILE)
        return

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    # Database ki tables check karo
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
    """)

    tables = [row[0] for row in cursor.fetchall()]

    print()
    print("Database tables:", tables)

    # -----------------------------------------------------
    # STUDENTS TABLE
    # -----------------------------------------------------

    if "students" in tables:

        cursor.execute("PRAGMA table_info(students)")
        columns = [row[1] for row in cursor.fetchall()]

        print("Students columns:", columns)

        # person_id / id column find karo
        id_column = None

        if "person_id" in columns:
            id_column = "person_id"
        elif "id" in columns:
            id_column = "id"

        # name column check
        if id_column and "name" in columns:

            for person_id, name in STUDENT_NAMES.items():

                cursor.execute(
                    f"""
                    UPDATE students
                    SET name = ?
                    WHERE {id_column} = ?
                    """,
                    (name, person_id)
                )

            print("Students table names updated.")

        else:
            print("Students table me required columns nahi mile.")

    else:
        print("students table nahi mila.")

    # -----------------------------------------------------
    # ATTENDANCE TABLE
    # -----------------------------------------------------

    if "attendance" in tables:

        cursor.execute("PRAGMA table_info(attendance)")
        columns = [row[1] for row in cursor.fetchall()]

        print("Attendance columns:", columns)

        if "person_id" in columns and "name" in columns:

            for person_id, name in STUDENT_NAMES.items():

                cursor.execute(
                    """
                    UPDATE attendance
                    SET name = ?
                    WHERE person_id = ?
                    """,
                    (name, person_id)
                )

            print("Attendance names updated.")

    connection.commit()
    connection.close()

    print("Database update complete.")


# =========================================================
# FIX CONFIG.PY
# =========================================================

def fix_config_names():

    if not CONFIG_FILE.exists():
        print("ERROR: config.py nahi mila.")
        print(CONFIG_FILE)
        return

    text = CONFIG_FILE.read_text(encoding="utf-8")

    new_names = """NAMES = {
    1: "Zulkar Nain",
    2: "Zulfikar",
    3: "Aakil"
}"""

    # Existing NAMES block replace karo
    pattern = r"NAMES\s*=\s*\{.*?\}"

    if re.search(pattern, text, re.DOTALL):

        text = re.sub(
            pattern,
            new_names,
            text,
            count=1,
            flags=re.DOTALL
        )

    else:

        if not text.endswith("\n"):
            text += "\n"

        text += "\n" + new_names + "\n"

    CONFIG_FILE.write_text(text, encoding="utf-8")

    print("config.py names updated.")


# =========================================================
# MAIN FUNCTION
# =========================================================

def fix_names():

    print()
    print("=" * 55)
    print("        STUDENT NAMES FIX")
    print("=" * 55)

    print()
    print("Names:")
    print("ID 1 -> Zulkar Nain")
    print("ID 2 -> Zulfikar")
    print("ID 3 -> Aakil")

    print()

    fix_database_names()

    print()

    fix_config_names()

    print()
    print("=" * 55)
    print("        STUDENT NAMES FIXED")
    print("=" * 55)
    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    fix_names()
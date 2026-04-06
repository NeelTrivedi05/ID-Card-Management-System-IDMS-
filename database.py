import sqlite3
import os

DB_NAME = "idcard.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            roll_no     TEXT    NOT NULL UNIQUE,
            department  TEXT    NOT NULL,
            year        TEXT    NOT NULL,
            contact     TEXT,
            email       TEXT,
            photo_path  TEXT,
            issue_date  TEXT    NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            employee_id   TEXT    NOT NULL UNIQUE,
            department    TEXT    NOT NULL,
            designation   TEXT    NOT NULL,
            contact       TEXT,
            email         TEXT,
            photo_path    TEXT,
            issue_date    TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# ── STUDENT CRUD ────────────────────────────────────────────

def add_student(name, roll_no, department, year, contact, email, photo_path, issue_date):
    try:
        conn = get_connection()
        conn.execute("""
            INSERT INTO students (name, roll_no, department, year, contact, email, photo_path, issue_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, roll_no, department, year, contact, email, photo_path, issue_date))
        conn.commit()
        conn.close()
        return True, "Student added successfully!"
    except sqlite3.IntegrityError:
        return False, f"Roll number '{roll_no}' already exists."
    except Exception as e:
        return False, str(e)

def get_all_students():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM students ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def search_students(query):
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM students
        WHERE name LIKE ? OR roll_no LIKE ? OR department LIKE ?
        ORDER BY name
    """, (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_student_by_id(student_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_student(student_id, name, roll_no, department, year, contact, email, photo_path, issue_date):
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE students
            SET name=?, roll_no=?, department=?, year=?, contact=?, email=?, photo_path=?, issue_date=?
            WHERE id=?
        """, (name, roll_no, department, year, contact, email, photo_path, issue_date, student_id))
        conn.commit()
        conn.close()
        return True, "Student updated successfully!"
    except sqlite3.IntegrityError:
        return False, f"Roll number '{roll_no}' already exists."
    except Exception as e:
        return False, str(e)

def delete_student(student_id):
    try:
        conn = get_connection()
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()
        return True, "Student deleted successfully!"
    except Exception as e:
        return False, str(e)

# ── STAFF CRUD ───────────────────────────────────────────────

def add_staff(name, employee_id, department, designation, contact, email, photo_path, issue_date):
    try:
        conn = get_connection()
        conn.execute("""
            INSERT INTO staff (name, employee_id, department, designation, contact, email, photo_path, issue_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, employee_id, department, designation, contact, email, photo_path, issue_date))
        conn.commit()
        conn.close()
        return True, "Staff member added successfully!"
    except sqlite3.IntegrityError:
        return False, f"Employee ID '{employee_id}' already exists."
    except Exception as e:
        return False, str(e)

def get_all_staff():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM staff ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def search_staff(query):
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM staff
        WHERE name LIKE ? OR employee_id LIKE ? OR department LIKE ?
        ORDER BY name
    """, (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_staff_by_id(staff_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM staff WHERE id = ?", (staff_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_staff(staff_id, name, employee_id, department, designation, contact, email, photo_path, issue_date):
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE staff
            SET name=?, employee_id=?, department=?, designation=?, contact=?, email=?, photo_path=?, issue_date=?
            WHERE id=?
        """, (name, employee_id, department, designation, contact, email, photo_path, issue_date, staff_id))
        conn.commit()
        conn.close()
        return True, "Staff updated successfully!"
    except sqlite3.IntegrityError:
        return False, f"Employee ID '{employee_id}' already exists."
    except Exception as e:
        return False, str(e)

def delete_staff(staff_id):
    try:
        conn = get_connection()
        conn.execute("DELETE FROM staff WHERE id = ?", (staff_id,))
        conn.commit()
        conn.close()
        return True, "Staff member deleted successfully!"
    except Exception as e:
        return False, str(e)

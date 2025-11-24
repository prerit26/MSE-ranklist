from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import sqlite3
import config

app = Flask(__name__)
CORS(app)


def get_connection():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def safe_get(row, *keys):
    if row is None:
        return None
    for key in keys:
        if key in row.keys():
            val = row[key]
            if val not in (None, "", "NULL"):
                return val
    return None


def dict_from_row(row):
    if row is None:
        return None
    d = dict(row)
    enr = safe_get(row, "enrollment_number", "Enrollment_Number")
    if enr:
        d["enrollment_number"] = enr
    return d


# ✅ NEW: Fetch subject mapping dynamically from DB
def get_subject_mapping(program, semester):
    conn = get_connection()
    
    query = """
    SELECT Subject_No, Subject_Name
    FROM Program_Subjects
    WHERE Program = ?
    AND Semester = ?
    """
    rows = conn.execute(query, (program, semester)).fetchall()
    conn.close()

    return {row["Subject_No"]: row["Subject_Name"] for row in rows}


# ✅ NEW: Apply DB-based subject mapping
def map_subject_names(student, program, semester):
    if not program or program == "all":
        return student

    mapping = get_subject_mapping(program, semester)

    mapped = {}
    for key, value in student.items():
        new_key = mapping.get(key, key)
        mapped[new_key] = value

    if "supp_subjects" in mapped:
        mapped["supp_subjects"] = [
            mapping.get(sub, sub) for sub in mapped["supp_subjects"]
        ]

    return mapped


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/classes")
def get_classes():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT DISTINCT class FROM {config.SEM_TABLES['1']['main']} ORDER BY class")
        rows = cursor.fetchall()
        classes = [row["class"] for row in rows if "class" in row.keys()]
        return jsonify(classes)
    except Exception as e:
        print("Error fetching classes:", e)
        return jsonify([]), 500
    finally:
        conn.close()


@app.route("/api/ranklist")
@app.route("/api/ranklist/<class_name>")
def get_ranklist(class_name=None):
    semester = request.args.get("semester", "1")
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if semester in ["1", "2"]:
            return handle_individual_semester(cursor, conn, semester, class_name)
        else:
            return handle_overall_semester(cursor, conn, class_name)
    except Exception as e:
        print("Error in get_ranklist:", e)
        import traceback
        traceback.print_exc()
        conn.close()
        return jsonify({"error": str(e)}), 500


def handle_individual_semester(cursor, conn, semester, class_name):
    sem_config = config.SEM_TABLES[semester]
    main_table = sem_config["main"]
    supp_table = sem_config["supp"]
    subjects = sem_config["subjects"]

    query = f"SELECT * FROM {main_table}"
    params = []
    if class_name and class_name != "all":
        query += " WHERE class = ?"
        params.append(class_name)

    cursor.execute(query, params)
    main_rows = cursor.fetchall()

    cursor.execute(f"SELECT * FROM {supp_table}")
    supp_rows = cursor.fetchall()

    supp_map = {}
    for row in supp_rows:
        enr = safe_get(row, "enrollment_number", "Enrollment_Number")
        if enr:
            supp_map[enr] = dict_from_row(row)

    students = []

    for row in main_rows:
        enr = safe_get(row, "enrollment_number", "Enrollment_Number")
        if not enr:
            continue

        supp = supp_map.get(enr)

        student = {
            "enrollment_number": enr,
            "student_name": safe_get(row, "student_name", "Student_Name"),
            "class": row["class"] if "class" in row.keys() else None,
            "supp_subjects": [],
        }

        student["gpa"] = safe_get(supp, "gpa", "GPA") if supp else None
        if not student["gpa"]:
            student["gpa"] = safe_get(row, "gpa", "GPA")

        student["cgpa"] = safe_get(supp, "cgpa", "CGPA") if supp else None
        if not student["cgpa"]:
            student["cgpa"] = safe_get(row, "cgpa", "CGPA")

        for sub in subjects:
            main_val = row[sub] if sub in row.keys() else None
            supp_val = supp[sub] if (supp and sub in supp.keys()) else None

            if supp_val not in (None, "", "NULL"):
                student[sub] = supp_val
                student["supp_subjects"].append(sub)
            else:
                student[sub] = main_val

        students.append(student)

    students.sort(key=lambda s: float(s["cgpa"] or 0), reverse=True)

    rank = 1
    for i in range(len(students)):
        if i > 0 and students[i]["cgpa"] != students[i - 1]["cgpa"]:
            rank = i + 1
        students[i]["rank"] = rank

    # ✅ Apply dynamic DB mapping
    students = [map_subject_names(s, class_name, int(semester)) for s in students]

    conn.close()
    return jsonify(students)


def handle_overall_semester(cursor, conn, class_name):
    sem1_subjects = config.SEM_TABLES["1"]["subjects"]
    sem2_subjects = config.SEM_TABLES["2"]["subjects"]

    # ---- Semester 1 ----
    cursor.execute(f"SELECT * FROM {config.SEM_TABLES['1']['main']}")
    sem1_main = cursor.fetchall()

    cursor.execute(f"SELECT * FROM {config.SEM_TABLES['1']['supp']}")
    sem1_supp = cursor.fetchall()

    sem1_map = {}
    for row in sem1_main:
        enr = safe_get(row, "enrollment_number", "Enrollment_Number")
        if enr:
            sem1_map[enr] = dict_from_row(row)

    for row in sem1_supp:
        enr = safe_get(row, "enrollment_number", "Enrollment_Number")
        if enr and enr in sem1_map:
            for k, v in dict(row).items():
                if v not in (None, "", "NULL"):
                    sem1_map[enr][k] = v

    # ---- Semester 2 ----
    cursor.execute(f"SELECT * FROM {config.SEM_TABLES['2']['main']}")
    sem2_main = cursor.fetchall()

    cursor.execute(f"SELECT * FROM {config.SEM_TABLES['2']['supp']}")
    sem2_supp = cursor.fetchall()

    sem2_map = {}
    for row in sem2_main:
        enr = safe_get(row, "enrollment_number", "Enrollment_Number")
        if enr:
            sem2_map[enr] = dict_from_row(row)

    for row in sem2_supp:
        enr = safe_get(row, "enrollment_number", "Enrollment_Number")
        if enr and enr in sem2_map:
            for k, v in dict(row).items():
                if v not in (None, "", "NULL"):
                    sem2_map[enr][k] = v

    # ---- Combine Sem1 + Sem2 ----
    students = []

    for enr, s1 in sem1_map.items():
        s2 = sem2_map.get(enr)
        if not s2:
            continue

        cg1 = safe_get(s1, "cgpa", "CGPA")
        cg2 = safe_get(s2, "cgpa", "CGPA")

        try:
            cg1_val = float(cg1) if cg1 else 0.0
            cg2_val = float(cg2) if cg2 else 0.0
        except:
            continue

        overall_cgpa = round(
            (cg1_val + cg2_val) / 2, 2
        ) if (cg1_val > 0 and cg2_val > 0) else 0.0

        student = {
            "enrollment_number": enr,
            "student_name": safe_get(s1, "student_name", "Student_Name"),
            "class": s1["class"] if "class" in s1.keys() else None,
            "cgpa": overall_cgpa,
            "gpa": overall_cgpa,
            "supp_subjects": [],
        }

        # Add Sem1 subjects (raw keys still here — will be mapped next)
        for sub in sem1_subjects:
            student[sub] = s1[sub] if sub in s1.keys() else None

        # Add Sem2 subjects (raw keys still here — will be mapped next)
        for sub in sem2_subjects:
            student[sub] = s2[sub] if sub in s2.keys() else None

        students.append(student)

    # ---- Class Filter ----
    if class_name and class_name != "all":
        students = [s for s in students if s.get("class") == class_name]

    # ---- Ranking ----
    students.sort(key=lambda s: s["cgpa"], reverse=True)

    rank = 1
    for i in range(len(students)):
        if i > 0 and students[i]["cgpa"] != students[i - 1]["cgpa"]:
            rank = i + 1
        students[i]["rank"] = rank

    # ✅ ✅ APPLY REAL SUBJECT NAMES
    # First map Sem1 subjects
    students = [map_subject_names(s, class_name, 1) for s in students]
    # Then map Sem2 subjects
    students = [map_subject_names(s, class_name, 2) for s in students]

    conn.close()
    return jsonify(students)



if __name__ == "__main__":
    app.run(debug=True, port=5000)

import sqlite3

# Path to your database
db_path = "student_results.db"

# Subject mapping taken from config.py
SUBJECT_MAP = {
    "EE": { 
        "Subject_2": "Resource and Environmental Economics",
        "Subject_4": "Econometric Methods",
        "Subject_3": "Environment Economy Interactions in the anthropocene",
        "Subject_5": "Indian Economic Development"
    },
    "AQF": { 
        "Subject_2": "Financial Mathematics",
        "Subject_4": "Econometric Methods",
        "Subject_3": "Financial Economics",
        "Subject_5": "Indian Economic Development"
    },
    "GE": { 
        "Subject_2": "Macroeconomics II",
        "Subject_4": "Econometric Methods",
        "Subject_3": "Public Economics",
        "Subject_5": "Indian Economic Development"
    },
    "FE": { 
        "Subject_5": "Indian Economic Development",
        "Subject_4": "Econometric Methods",
        "Subject_3": "Financial Economics I",
        "Subject_2": "Financial Mathematics"
    },
    "AE": { 
        "Subject_2": "Financial Economics",
        "Subject_3": "Econometric Methods",
        "Subject_4": "Indian Economic Development",
        "Subject_5": "Financial Mathematics"
    }
}

# Connect to DB
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1️⃣ Create the mapping table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Program_Subjects (
        Program TEXT,
        Semester INTEGER,
        Subject_No TEXT,
        Subject_Name TEXT
    );
""")

# 2️⃣ Insert mapping rows for Semester 2
for program, subjects in SUBJECT_MAP.items():
    for subject_no, subject_name in subjects.items():
        cursor.execute("""
            INSERT INTO Program_Subjects (Program, Semester, Subject_No, Subject_Name)
            VALUES (?, ?, ?, ?)
        """, (program, 2, subject_no, subject_name))

# Save changes
conn.commit()
conn.close()

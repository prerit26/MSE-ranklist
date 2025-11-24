# config.py

DB_PATH = "student_results.db"

# ✅ Database Tables Configuration
SEM_TABLES = {
    "1": {
        "main": "Batch_2024_26_1st_sem",
        "supp": "Batch_2024_26_1st_sem_Supplementary",
        "subjects": ["microeconomics_1", "macroeconomics_1", "math_statistics", "math_methods"]
    },
    "2": {
        "main": "Batch_2024_26_2nd_sem",
        "supp": "Batch_2024_26_2nd_sem_supplemantary",
        "subjects": ["microeconomics_2", "Subject_2", "Subject_3", "Subject_4", "Subject_5"]
    },
    # ✅ NEW: Overall Configuration
    "overall": {
        "main": "merged_results",       # Pulls from the combined table
        "supp": "all_supp_results",     # Pulls from the combined supplementary table
        "subjects": [
            # These must match the column names in your 'merged_results' table.
            # Currently based on your DB, it contains Sem 1 subjects.
            "microeconomics_1", 
            "macroeconomics_1", 
            "math_statistics", 
            "math_methods"
            # If you add Sem 2 columns to the 'merged_results' table later, add them here.
        ]
    }
}

# ✅ Subject Mapping Filter (Semester 2)
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
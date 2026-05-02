import sqlite3
from typing import List, Dict

DB_PATH = "app/data/doctors.db"

def hospital_db_tool(specialty: str, location: str) -> List[Dict]:
    """
    Fetch doctors based on specialty and location.

    Args:
        specialty (str): medical specialty
        location (str): city/hospital location

    Returns:
        List of doctors
    """

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = """
        SELECT name, specialty, hospital, location, available_days
        FROM doctors
        WHERE LOWER(specialty) LIKE ?
        AND LOWER(location) LIKE ?
        """

        cursor.execute(query, (f"%{specialty.lower()}%", f"%{location.lower()}%"))

        rows = cursor.fetchall()

        conn.close()

        if not rows:
            return []

        return [
            {
                "name": row[0],
                "specialty": row[1],
                "hospital": row[2],
                "location": row[3],
                "available_days": row[4].split(",")
            }
            for row in rows
        ]

    except Exception as e:
        print(f"DB Error: {e}")
        return []
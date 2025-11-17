import os
import pymysql
from typing import List, Dict, Any

def get_mysql_connection():
    """
    Establish a connection to the MySQL database.
    Uses environment variables if provided; falls back to localhost.
    """
    try:
        conn = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "Ian910504#"),
            db=os.getenv("MYSQL_DB", "academicworld"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"⚠️ MySQL connection failed: {e}")
        return None


def get_top_faculty_krc_full(limit: int = 25) -> List[Dict[str, Any]]:
    """Get top faculty by KRC score. Returns a list of dictionaries."""
    query = """
    SELECT 
        f.name AS faculty_name,
        k.name AS keyword,
        u.name AS university,
        SUM(pk.score * pub.num_citations) AS krc
    FROM faculty f
    JOIN faculty_publication fp ON f.id = fp.faculty_id
    JOIN publication pub ON fp.publication_id = pub.id
    JOIN publication_keyword pk ON pub.id = pk.publication_id
    JOIN keyword k ON pk.keyword_id = k.id
    JOIN university u ON f.university_id = u.id
    GROUP BY f.id, k.id
    ORDER BY f.name, krc DESC
    """
    conn = get_mysql_connection()
    if not conn:
        return []  # fallback if DB not reachable

    try:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    except Exception as e:
        print(f"❌ Error fetching KRC: {e}")
        return []
    finally:
        conn.close()

    # Keep only top KRC per faculty
    top_krc_by_faculty = {}
    for row in rows:
        faculty_name = row["faculty_name"]
        krc = row["krc"]
        if faculty_name not in top_krc_by_faculty or krc > top_krc_by_faculty[faculty_name]["krc"]:
            top_krc_by_faculty[faculty_name] = row

    sorted_rows = sorted(top_krc_by_faculty.values(), key=lambda x: x["krc"], reverse=True)
    return sorted_rows[:limit]


def update_faculty_interest(name: str, new_interest: str) -> Dict[str, Any]:
    """Update a faculty's research interest."""
    conn = get_mysql_connection()
    if not conn:
        return {"success": False, "message": "Database not connected."}

    query = "UPDATE faculty SET research_interest = %s WHERE name = %s"
    try:
        with conn.cursor() as cur:
            cur.execute(query, (new_interest, name))
            conn.commit()
            updated = cur.rowcount > 0
            if updated:
                return {"success": True, "message": f"Updated interest for {name}."}
            else:
                return {"success": False, "message": f"No faculty found with name {name}."}
    except Exception as e:
        print(f"❌ Error updating faculty interest: {e}")
        return {"success": False, "message": f"DB error: {e}"}
    finally:
        conn.close()


def get_faculty_analytics(limit=20) -> List[Dict[str, Any]]:
    """Return top faculty analytics with name, position, email, and publication count."""
    query = """
        SELECT 
            f.name, 
            f.position, 
            f.email, 
            u.name AS university, 
            COUNT(fp.publication_id) AS publication_count
        FROM faculty f
        LEFT JOIN faculty_publication fp ON f.id = fp.faculty_id
        LEFT JOIN university u ON f.university_id = u.id
        GROUP BY f.id, f.name, f.position, f.email, u.name
        ORDER BY publication_count DESC, f.name ASC
        LIMIT %s
    """
    conn = get_mysql_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()
    except Exception as e:
        print(f"❌ Error fetching faculty analytics: {e}")
        return []
    finally:
        conn.close()

    result = []
    for row in rows:
        faculty_data = {
            "name": row["name"],
            "position": row["position"],
            "email": row["email"],
            "university": row["university"],
            "publication_count": row["publication_count"]
        }
        result.append(faculty_data)
    return result


def update_faculty_position(name: str, new_position: str) -> Dict[str, Any]:
    """Update the position/title of a faculty member by name."""
    conn = get_mysql_connection()
    if not conn:
        return {"error": "Database not connected."}

    query = "UPDATE faculty SET position = %s WHERE name = %s"
    try:
        with conn.cursor() as cur:
            cur.execute(query, (new_position, name))
            conn.commit()
            if cur.rowcount == 0:
                return {"error": f"No faculty found with name '{name}'."}
            cur.execute("SELECT name, position, email FROM faculty WHERE name = %s", (name,))
            row = cur.fetchone()
            return row or {"error": "Updated but could not fetch record."}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

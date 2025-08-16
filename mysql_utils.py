import pymysql
from typing import List, Dict, Any, Optional

def get_mysql_connection():
    """Establish a connection to the MySQL database."""
    return pymysql.connect(
        host="localhost",
        user="root",           # change if needed
        password="Ian910504#", # your password
        db="academicworld",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor    # returns dictionaries!
    )

def get_top_faculty_krc_full(limit: int = 25) -> List[Dict[str, Any]]:
    """
    Get top faculty by KRC (Keyword Relevance-Citation) score.
    Returns a list of dictionaries, one per faculty.
    """
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
    try:
        conn = get_mysql_connection()
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

    # Sort top faculty by KRC and return top N
    sorted_rows = sorted(top_krc_by_faculty.values(), key=lambda x: x["krc"], reverse=True)
    return sorted_rows[:limit]

def update_faculty_interest(name: str, new_interest: str) -> Dict[str, Any]:
    """
    Update a faculty's research interest.
    Returns {'success': True/False, 'message': ...}
    """
    query = "UPDATE faculty SET research_interest = %s WHERE name = %s"
    try:
        conn = get_mysql_connection()
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
    """
    Return top faculty analytics with name, position, email, and publication count.
    """
    # Simplified query - remove the extra fields that might cause grouping issues
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
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()
    except Exception as e:
        print(f"❌ Error fetching faculty analytics: {e}")
        return []
    finally:
        conn.close()
    
    # Debug: Print first few rows to see what we're getting
    print("Debug - First few raw rows:")
    for i, row in enumerate(rows[:3]):
        print(f"Row {i}: name='{row['name']}', email='{row['email']}', university='{row['university']}', position='{row['position']}'")
    
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
        
        # Debug: Print first few processed results
        if len(result) <= 3:
            print(f"Debug - Processed faculty data: {faculty_data}")
    
    return result

def update_faculty_position(name: str, new_position: str) -> Dict[str, Any]:
    """
    Update the position/title of a faculty member by name.
    Returns dict with name, position, email (on success) or {'error': ...}
    """
    query = "UPDATE faculty SET position = %s WHERE name = %s"
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cur:
            cur.execute(query, (new_position, name))
            conn.commit()
            if cur.rowcount == 0:
                return {"error": f"No faculty found with name '{name}'."}
            # Get updated info
            cur.execute("SELECT name, position, email FROM faculty WHERE name = %s", (name,))
            row = cur.fetchone()
            if row:
                return {
                    "name": row["name"],
                    "position": row["position"],
                    "email": row["email"]
                }
            else:
                return {"error": "Faculty updated, but could not retrieve updated info."}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()



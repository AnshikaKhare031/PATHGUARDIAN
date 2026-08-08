import psycopg2
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "config", ".env"))
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)


def get_score_for_point(lat, lng):
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT s.score
        FROM grid_cells g
        JOIN safety_scores s ON s.cell_id = g.id
        WHERE ST_Contains(g.cell_geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        LIMIT 1;
    """
    
    cur.execute(query, (lng, lat))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return result[0]
    else:
        return None



def get_reports_near(lat, lng, radius_meters):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT id, category, description, reported_at
        FROM user_reports
        WHERE ST_DWithin(
            location::geography,
            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
            %s
        );
    """

    cur.execute(query, (lng, lat, radius_meters))
    results = cur.fetchall()

    cur.close()
    conn.close()

    return results



def insert_report(lat, lng, category, description):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        INSERT INTO user_reports (location, category, description)
        VALUES (ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s)
        RETURNING id;
    """

    cur.execute(query, (lng, lat, category, description))
    new_id = cur.fetchone()[0]

    conn.commit()

    cur.close()
    conn.close()

    return new_id

if __name__ == "__main__":
    test_lat = 26.4499
    test_lng = 80.3319

    score = get_score_for_point(test_lat, test_lng)
    print("Safety score at that point:", score)

    reports = get_reports_near(test_lat, test_lng, 1000)
    print("Reports within 1km:", reports)

    new_report_id = insert_report(
        test_lat,
        test_lng,
        "poor_lighting",
        "Streetlight not working near this junction"
    )
    print("New report inserted with ID:", new_report_id)
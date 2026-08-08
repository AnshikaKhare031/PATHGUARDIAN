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


if __name__ == "__main__":
    test_lat = 26.4499
    test_lng = 80.3319

    score = get_score_for_point(test_lat, test_lng)
    print("Safety score at that point:", score)
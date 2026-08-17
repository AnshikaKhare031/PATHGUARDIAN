import psycopg2
from dotenv import load_dotenv
import os
import h3

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "config", ".env"))
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def seed_police_stations():
    conn = get_connection()
    cur = conn.cursor()

    stations = [
        ("Kotwali Police Station", 80.3319, 26.4670),
        ("Colonelganj Police Station", 80.3462, 26.4560),
        ("Govind Nagar Police Station", 80.3020, 26.4390),
    ]

    for name, lng, lat in stations:
        cur.execute("""
            INSERT INTO police_stations (name, location)
            VALUES (%s, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
        """, (name, lng, lat))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(stations)} police stations")

def seed_streetlights():
    conn = get_connection()
    cur = conn.cursor()

    streetlights = [
        (80.3300, 26.4650),
        (80.3350, 26.4680),
        (80.3280, 26.4600),
        (80.3400, 26.4550),
        (80.3250, 26.4500),
    ]

    for lng, lat in streetlights:
        cur.execute("""
            INSERT INTO streetlights (location)
            VALUES (ST_SetSRID(ST_MakePoint(%s, %s), 4326));
        """, (lng, lat))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(streetlights)} streetlights")

def seed_streetlights():
    conn = get_connection()
    cur = conn.cursor()

    streetlights = [
        (80.3300, 26.4650),
        (80.3350, 26.4680),
        (80.3280, 26.4600),
        (80.3400, 26.4550),
        (80.3250, 26.4500),
    ]

    for lng, lat in streetlights:
        cur.execute("""
            INSERT INTO streetlights (location)
            VALUES (ST_SetSRID(ST_MakePoint(%s, %s), 4326));
        """, (lng, lat))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(streetlights)} streetlights")


def seed_streetlights():
    conn = get_connection()
    cur = conn.cursor()

    streetlights = [
        (80.3300, 26.4650),
        (80.3350, 26.4680),
        (80.3280, 26.4600),
        (80.3400, 26.4550),
        (80.3250, 26.4500),
    ]

    for lng, lat in streetlights:
        cur.execute("""
            INSERT INTO streetlights (location)
            VALUES (ST_SetSRID(ST_MakePoint(%s, %s), 4326));
        """, (lng, lat))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(streetlights)} streetlights")


def seed_streetlights():
    conn = get_connection()
    cur = conn.cursor()

    streetlights = [
        (80.3300, 26.4650),
        (80.3350, 26.4680),
        (80.3280, 26.4600),
        (80.3400, 26.4550),
        (80.3250, 26.4500),
    ]

    for lng, lat in streetlights:
        cur.execute("""
                    INSERT INTO streetlights (location)
                    VALUES (ST_SetSRID(ST_MakePoint(%s, %s), 4326));
                """, (lng, lat))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(streetlights)} streetlights")
    


def seed_grid_cells_and_scores():
    conn = get_connection()
    cur = conn.cursor()

    locations = [
        (26.4670, 80.3319, 85),
        (26.4560, 80.3462, 40),
        (26.4390, 80.3020, 70),
        (26.4550, 80.3400, 55),
    ]

    for lat, lng, score in locations:
        hex_id = h3.latlng_to_cell(lat, lng, 9)
        center_lat, center_lng = h3.cell_to_latlng(hex_id)

        cur.execute("""
            INSERT INTO grid_cells (h3_index, center_point)
            VALUES (%s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            ON CONFLICT (h3_index) DO NOTHING
            RETURNING id;
        """, (hex_id, center_lng, center_lat))

        result = cur.fetchone()
        if result:
            cell_id = result[0]
            cur.execute("""
                INSERT INTO safety_scores (cell_id, score)
                VALUES (%s, %s);
            """, (cell_id, score))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Processed {len(locations)} H3 grid cells with scores")


if __name__ == "__main__":
    seed_police_stations()
    seed_streetlights()
    seed_grid_cells_and_scores()  



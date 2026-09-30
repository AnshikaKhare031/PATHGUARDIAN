import psycopg2
from dotenv import load_dotenv
import os
import h3
import json

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

def load_real_signals():
    conn = get_connection()
    cur = conn.cursor()

    json_path = os.path.join(
        os.path.dirname(__file__), "..", "..",
        "backend", "app", "data", "proxy_signals_kanpur.json"
    )

    with open(json_path, "r") as f:
        data = json.load(f)

    streetlight_count = 0
    police_count = 0
    poi_count = 0
    report_count = 0

    for signal in data:
        signal_type = signal["signal_type"]
        lat = signal["latitude"]
        lng = signal["longitude"]

        if signal_type == "streetlight":
            cur.execute("""
                INSERT INTO streetlights(location)
                VALUES (ST_SetSRID(ST_MakePoint(%s,%s), 4326))
                ON CONFLICT (location) DO NOTHING;
                """, (lng, lat))
            streetlight_count += 1

        elif signal_type == "police_station":
            cur.execute("""
                INSERT INTO police_stations(name, location)
                VALUES (%s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                ON CONFLICT (location) DO NOTHING;
                """, (signal.get("name", "Unknown"), lng, lat))
            police_count += 1

        elif signal_type == "foot_traffic":
            cur.execute("""
                INSERT INTO points_of_interest (name, category, location)
                VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                ON CONFLICT (location) DO NOTHING;
                """, ("Foot traffic signal", "foot_traffic", lng, lat))
            poi_count += 1

        elif signal_type == "user_report":
            cur.execute("""
                INSERT INTO user_reports(location, category, description)
                VALUES (ST_SetSRID(ST_MakePoint(%s,  %s), 4326), %s, %s);
                """, (lng, lat, signal["category"], "Imported from verified signal dataset"))
            report_count += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"Loaded {streetlight_count} streetlights")
    print(f"Loaded {police_count} police stations")
    print(f"Loaded {poi_count} foot traffic points")
    print(f"Loaded {report_count} user reports")



if __name__ == "__main__": 
    load_real_signals()



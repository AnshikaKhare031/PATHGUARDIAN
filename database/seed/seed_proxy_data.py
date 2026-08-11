import psycopg2
from dotenv import load_dotenv
import os

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

if __name__ == "__main__":
    seed_police_stations()
    seed_streetlights()
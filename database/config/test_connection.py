import psycopg2
from dotenv import load_dotenv
import os

# Explicitly point to the .env file's location
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")


try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT PostGIS_version();")
    result = cur.fetchone()
    print("Connected successfully!")
    print("PostGIS version:", result)
    cur.close()
    conn.close()
except Exception as e:
    print("Connection failed:", e)
# Database Setup — PathGuardian

This project uses **Supabase** (hosted PostgreSQL + PostGIS) as its shared database.

## How to connect locally

1. Ask Pratiti for the database password (not stored here for security).
2. In `database/config/`, create a file named `.env` (this is gitignored — never commit it).
3. Add this line, replacing the password:
DATABASE_URL=postgresql://postgres.sozsfnyhonfnfnulrenf:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres

Install dependencies:
pip install psycopg2-binary python-dotenv h3

Test your connection:
python database/config/test_connection.py

   You should see "Connected successfully!" and a PostGIS version number.

## Database Schema

We use **H3 hexagonal indexing** (resolution 9) for spatial grid cells instead of manual polygons.

### Tables

- **grid_cells** — H3 hexagon cells covering the map. Key column: `h3_index` (text, unique).
- **safety_scores** — one score per grid cell, linked via `cell_id`.
- **user_reports** — anonymous user-submitted incidents. `category` is restricted to exactly 4 values: `poor_lighting`, `harassment`, `suspicious_activity`, `other`.
- **police_stations**, **streetlights**, **points_of_interest** — reference/proxy signal data.

### Security (RLS)
All tables have Row Level Security enabled:
- Public **read** access on all tables
- Public **insert** access on `user_reports` only (anonymous reporting)
- Updates/deletes restricted to service role / admin

## Available Functions (`database/geospatial/spatial_queries.py`)

| Function | Purpose |
|---|---|
| `get_score_for_point(lat, lng)` | Returns the safety score for a location, or `None` if no data exists there |
| `get_reports_near(lat, lng, radius_meters)` | Returns all reports within a radius of a point |
| `get_scores_for_points(points)` | Given a list of (lat, lng) tuples, returns scores for each — built for the routing engine |
| `insert_report(lat, lng, category, description)` | Adds a new user report, returns its new ID |
| `delete_report(report_id)` | Deletes a report by ID, returns True/False |

All functions are tested against live seed data. Run the file directly to see example usage:
python database/geospatial/spatial_queries.py


## Test/Seed Data

`database/seed/seed_proxy_data.py` populates the database with sample data for local testing:
- 3 fake police stations
- 5 fake streetlights
- 4 fake grid cells with safety scores (near real Kanpur locations)

Run it with:
python database/seed/seed_proxy_data.py
-- PathGuardian Database Schema
-- Reviewed and finalized with team (grid: H3 resolution 9, anonymous reporting, static scoring for MVP)

CREATE TABLE grid_cells (
    id SERIAL PRIMARY KEY,
    h3_index TEXT UNIQUE,                          -- H3 hexagon index, resolution 9
    cell_geom GEOMETRY(Polygon, 4326),              -- optional, legacy/reference only
    center_point GEOMETRY(Point, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_grid_cells_geom ON grid_cells USING GIST (cell_geom);
CREATE INDEX idx_grid_cells_center ON grid_cells USING GIST (center_point);
CREATE INDEX idx_grid_cells_h3 ON grid_cells (h3_index);


CREATE TABLE safety_scores (
    id SERIAL PRIMARY KEY,
    cell_id INTEGER REFERENCES grid_cells(id) NOT NULL,
    score FLOAT NOT NULL CHECK (score >= 0 AND score <= 100),
    streetlight_component FLOAT,
    police_component FLOAT,
    foot_traffic_component FLOAT,
    report_component FLOAT,
    time_of_day TEXT,  -- not used in MVP; static score only, flagged as Phase 2 roadmap feature
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_safety_scores_cell ON safety_scores (cell_id);


CREATE TABLE user_reports (
    id SERIAL PRIMARY KEY,
    location GEOMETRY(Point, 4326) NOT NULL,
    cell_id INTEGER REFERENCES grid_cells(id),
    category TEXT NOT NULL CHECK (category IN ('poor_lighting', 'harassment', 'suspicious_activity', 'other')),
    description TEXT,
    reported_at TIMESTAMP DEFAULT NOW(),
    is_verified BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_user_reports_location ON user_reports USING GIST (location);
CREATE INDEX idx_user_reports_cell ON user_reports (cell_id);


CREATE TABLE police_stations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location GEOMETRY(Point, 4326) NOT NULL,
    source TEXT DEFAULT 'osm',
    UNIQUE (location)
);

CREATE INDEX idx_police_stations_location ON police_stations USING GIST (location);


CREATE TABLE streetlights (
    id SERIAL PRIMARY KEY,
    location GEOMETRY(Point, 4326) NOT NULL,
    source TEXT DEFAULT 'osm',
    UNIQUE (location)
);

CREATE INDEX idx_streetlights_location ON streetlights USING GIST (location);


CREATE TABLE points_of_interest (
    id SERIAL PRIMARY KEY,
    name TEXT,
    category TEXT,  -- e.g. 'foot_traffic', 'shop', 'transit_stop' — NOT the report category list
    location GEOMETRY(Point, 4326) NOT NULL,
    source TEXT DEFAULT 'osm',
    UNIQUE (location)
);

CREATE INDEX idx_poi_location ON points_of_interest USING GIST (location);

ALTER TABLE grid_cells ENABLE ROW LEVEL SECURITY;
ALTER TABLE safety_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE police_stations ENABLE ROW LEVEL SECURITY;
ALTER TABLE streetlights ENABLE ROW LEVEL SECURITY;
ALTER TABLE points_of_interest ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public can view grid cells" ON grid_cells FOR SELECT USING (true);
CREATE POLICY "Public can view safety scores" ON safety_scores FOR SELECT USING (true);
CREATE POLICY "Public can view police stations" ON police_stations FOR SELECT USING (true);
CREATE POLICY "Public can view streetlights" ON streetlights FOR SELECT USING (true);
CREATE POLICY "Public can view points of interest" ON points_of_interest FOR SELECT USING (true);

CREATE POLICY "Public can view reports" ON user_reports FOR SELECT USING (true);
CREATE POLICY "Public can submit reports" ON user_reports FOR INSERT WITH CHECK (true);
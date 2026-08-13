 -- DRAFT SCHEMA — pending team review, not final
 
CREATE TABLE grid_cells (
    id SERIAL PRIMARY KEY,
    cell_geom GEOMETRY(Polygon, 4326) NOT NULL,   -- the cell's boundary
    center_point GEOMETRY(Point, 4326) NOT NULL,   -- quick lookup without computing centroid every time
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_grid_cells_geom ON grid_cells USING GIST (cell_geom);
CREATE INDEX idx_grid_cells_center ON grid_cells USING GIST (center_point);


CREATE TABLE safety_scores (
    id SERIAL PRIMARY KEY,
    cell_id INTEGER REFERENCES grid_cells(id) NOT NULL,
    score FLOAT NOT NULL CHECK (score >= 0 AND score <= 100),
    streetlight_component FLOAT,
    police_component FLOAT,
    foot_traffic_component FLOAT,
    report_component FLOAT,
    time_of_day TEXT,  -- e.g. 'morning', 'evening', 'night' -- ask Team Lead if this is needed
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_safety_scores_cell ON safety_scores (cell_id);


CREATE TABLE user_reports (
    id SERIAL PRIMARY KEY,
    location GEOMETRY(Point, 4326) NOT NULL,
    cell_id INTEGER REFERENCES grid_cells(id),
    category TEXT NOT NULL,  -- e.g. 'poor_lighting', 'harassment', 'suspicious_activity', 'other'
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
    source TEXT DEFAULT 'osm'
);

CREATE INDEX idx_police_stations_location ON police_stations USING GIST (location);

CREATE TABLE streetlights (
    id SERIAL PRIMARY KEY,
    location GEOMETRY(Point, 4326) NOT NULL,
    source TEXT DEFAULT 'osm'
);

CREATE INDEX idx_streetlights_location ON streetlights USING GIST (location);

CREATE TABLE points_of_interest (
    id SERIAL PRIMARY KEY,
    name TEXT,
    category TEXT NOT NULL CHECK (category IN ('poor_lighting', 'harassment', 'suspicious_activity', 'other')),
    location GEOMETRY(Point, 4326) NOT NULL,
    source TEXT DEFAULT 'osm'
);

CREATE INDEX idx_poi_location ON points_of_interest USING GIST (location);
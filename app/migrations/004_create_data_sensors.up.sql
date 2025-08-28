CREATE TABLE IF NOT EXISTS data_sensors (
    id SERIAL PRIMARY KEY,
    label VARCHAR(100),
    name VARCHAR(100),
    unit VARCHAR(100),
    status BOOLEAN DEFAULT TRUE,
    timestamp TIMESTAMP
)

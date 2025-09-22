CREATE TABLE ugm25_predictions
(
    id          NUMBER GENERATED ALWAYS AS IDENTITY
        (START WITH 1 INCREMENT BY 1)
        PRIMARY KEY,
    sensor_id   NUMBER,
    record_time TIMESTAMP WITH TIME ZONE,
    value       VARCHAR2(20 CHAR),
    created_at  TIMESTAMP,
    updated_at  TIMESTAMP
);
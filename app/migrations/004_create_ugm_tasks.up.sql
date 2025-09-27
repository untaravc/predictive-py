CREATE TABLE ugm25_tasks
(
    id          NUMBER GENERATED ALWAYS AS IDENTITY
        (START WITH 1 INCREMENT BY 1)
        PRIMARY KEY,
    category   VARCHAR2(100 CHAR), -- record, predict, upload
    sensor_id   NUMBER,
    start_at    TIMESTAMP WITH TIME ZONE,
    is_complete  CHAR(1) CHECK (is_complete IN (0, 1, 2)),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
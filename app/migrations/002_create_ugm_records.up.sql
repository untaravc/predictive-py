CREATE TABLE ugm25_records
(
    id          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensor_id   NUMBER               NOT NULL,
    record_time DATE                 NOT NULL,
    value       FLOAT,
    created_at  DATE DEFAULT SYSDATE NOT NULL,
    updated_at  DATE
);
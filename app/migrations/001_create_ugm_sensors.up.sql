CREATE TABLE ugm_sensors
(
    id         NUMBER PRIMARY KEY,
    web_id     VARCHAR2(200 CHAR),
    name       VARCHAR2(255 CHAR),
    path       VARCHAR2(500 CHAR),
    descriptor VARCHAR2(500 CHAR),
    is_active  CHAR(1) CHECK (is_active IN (1, 0)),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
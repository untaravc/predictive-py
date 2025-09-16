CREATE TABLE pi_points
(
    id                NUMBER,
    web_id            VARCHAR2(200 CHAR) PRIMARY KEY,
    name              VARCHAR2(255 CHAR),
    path              VARCHAR2(500 CHAR),
    descriptor        VARCHAR2(500 CHAR),
    point_class       VARCHAR2(50 CHAR),
    point_type        VARCHAR2(50 CHAR),
    digital_set_name  VARCHAR2(100 CHAR),
    engineering_units VARCHAR2(50 CHAR),
    span              NUMBER(10,4),
    zero_val          NUMBER(10,4),
    step              CHAR(1) CHECK (step IN ('Y', 'N')),
    future            CHAR(1) CHECK (future IN ('Y', 'N')),
    display_digits    NUMBER,
    created_at        TIMESTAMP,
    updated_at        TIMESTAMP
}
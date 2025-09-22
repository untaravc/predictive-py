CREATE TABLE ugm25_task
(
    id          NUMBER GENERATED ALWAYS AS IDENTITY
        (START WITH 1 INCREMENT BY 1)
        PRIMARY KEY,
    category   VARCHAR2(100 CHAR),
    name       VARCHAR2(100 CHAR),
    is_complete  CHAR(1) CHECK (is_active IN (1, 0)),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
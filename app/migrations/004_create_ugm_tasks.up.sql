CREATE TABLE ugm25_tasks
(
    id          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category    VARCHAR2(100), -- record, predict, upload
    params      VARCHAR2(100),
    start_at    DATE NOT NULL,
    is_complete CHAR(1) CHECK (is_complete IN (0, 1, 2)),
    created_at  DATE DEFAULT SYSDATE NOT NULL,
    updated_at  DATE
);
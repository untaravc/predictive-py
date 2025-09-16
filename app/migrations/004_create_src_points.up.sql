-- web_id 
--     Id:,
--     Name: 
--     Path:
--     Descriptor:
--     PointClass:
--     PointType:
--     DigitalSetName:
--     EngineeringUnits:
--     Span:
--     Zero:
--     Step:,
--     Future:,
--     DisplayDigits:,

CREATE TABLE IF NOT EXISTS src_points (
    id BIGINT PRIMARY KEY,
    web_id VARCHAR(50) ,
    name VARCHAR(50) ,
    path VARCHAR(50) ,
    descriptor VARCHAR(50) ,
    point_class VARCHAR(50) ,
    point_type VARCHAR(50) ,
    digital_set_name VARCHAR(50) ,
    engineering_units VARCHAR(50) ,
    span VARCHAR(50) ,
    zero VARCHAR(50) ,
    step VARCHAR(50) ,
    future VARCHAR(50) ,
    display_digits VARCHAR(50) 
)

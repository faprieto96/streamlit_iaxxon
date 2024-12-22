

CREATE TABLE sosein_automatization.sensor_data_iaxxon (
    id INT AUTO_INCREMENT PRIMARY KEY, -- Unique identifier for each record
    TCAP DECIMAL(10,2),                -- Stores the TCAP value (up to 2 decimal places)
    TEXT DECIMAL(10,2),                -- Stores the TEXT value (up to 2 decimal places)
    TDAC DECIMAL(10,2),                -- Stores the TDAC value (up to 2 decimal places)
    TINT DECIMAL(10,2),                -- Stores the TINT value (up to 2 decimal places)
    TAC1 DECIMAL(10,2),                -- Stores the TAC1 value (up to 2 decimal places)
    TRET DECIMAL(10,2),                -- Stores the TRET value (up to 2 decimal places)
    fan TINYINT,                       -- Binary state for fan (1 or 0)
    pump TINYINT,                      -- Binary state for pump (1 or 0)
    heat TINYINT,                      -- Binary state for heat (1 or 0)
    datetime DATETIME DEFAULT CURRENT_TIMESTAMP,        -- Timestamp for the data
    instalacion VARCHAR(255)          -- Installation identifier (e.g., "sosein_prueba")
);


INSERT INTO sosein_automatization.sensor_data_iaxxon (
    TCAP, TEXT, TDAC, TINT, TAC1, TRET, fan, pump, heat, instalacion
) VALUES (
    97.94, 36.31, 52.56, 58.44, 54.69, 54.75, 1, 1, 0, 'sosein_prueba'
);

select * from sosein_automatization.sensor_data_iaxxon order by datetime desc
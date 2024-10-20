CREATE TABLE payments (
    id SERIAL PRIMARY KEY,  -- Identificador único autoincremental para cada registro
    payment_at TIMESTAMP,  -- Fecha y hora de la transacción
    company_code VARCHAR(20) NOT NULL,  -- Código alfanumérico de la empresa
    status VARCHAR(20) NOT NULL,  -- Estado de la transacción (p.ej., 'confirmed')
    amount NUMERIC(15, 2) NOT NULL,  -- Cantidad facturada (número decimal con 2 decimales)
    external_client_id VARCHAR(50),  -- Identificador del cliente externo
    created_at TIMESTAMP NOT NULL,  -- Fecha y hora de creación del registro
    updated_at TIMESTAMP NOT NULL  -- Fecha y hora de la última actualización
);

CREATE TABLE companies (
    id SERIAL PRIMARY KEY,                    -- Identificador único para cada compañía
    company_code VARCHAR(50) NOT NULL,        -- Código de la compañía
    company_name VARCHAR(255) NOT NULL,       -- Nombre de la compañía
    category_id INTEGER,                      -- Identificador de la categoría
    category_name VARCHAR(255),               -- Nombre de la categoría
    is_top_biller BOOLEAN DEFAULT FALSE       -- Indica si es un "top biller"
);
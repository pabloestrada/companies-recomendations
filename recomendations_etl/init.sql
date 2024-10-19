CREATE DATABASE test_api_db;
CREATE USER api WITH ENCRYPTED PASSWORD 'test';
GRANT ALL PRIVILEGES ON DATABASE test_api_db TO api;

CREATE DATABASE recomendations_db;
CREATE USER recomendations_user WITH ENCRYPTED PASSWORD 'test';
GRANT ALL PRIVILEGES ON DATABASE recomendations_db TO recomendations_user;

GRANT ALL PRIVILEGES ON DATABASE recomendations_db TO airflow;

\c recomendations_db;

CREATE TABLE data_updates (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    last_date_update DATE NOT NULL DEFAULT CURRENT_DATE,  -- Cambiado a DATE
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- Crear la función que actualizará el campo updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear el trigger que ejecuta la función después de cada INSERT o UPDATE
CREATE TRIGGER set_updated_at
BEFORE INSERT OR UPDATE ON data_updates
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE data_updates
ADD CONSTRAINT unique_service_name_last_date UNIQUE (service_name, last_date_update);

CREATE TABLE payments_l0 (
    id SERIAL PRIMARY KEY,  -- Identificador único autoincremental para cada registro
    payment_id VARCHAR(50) NOT NULL,  -- Identificador del pago
    payment_at TIMESTAMP,  -- Fecha y hora de la transacción
    company_code VARCHAR(20) NOT NULL,  -- Código alfanumérico de la empresa
    status VARCHAR(20) NOT NULL,  -- Estado de la transacción (p.ej., 'confirmed')
    amount NUMERIC(15, 2) NOT NULL,  -- Cantidad facturada (número decimal con 2 decimales)
    external_client_id VARCHAR(50),  -- Identificador del cliente externo
    created_at TIMESTAMP NOT NULL,  -- Fecha y hora de creación del registro
    updated_at TIMESTAMP NOT NULL,  -- Fecha y hora de la última actualización
    start_date TIMESTAMP NOT NULL DEFAULT NOW(),  -- Fecha de inicio de validez del registro
    end_date TIMESTAMP DEFAULT NULL,  -- Fecha de fin de validez del registro (NULL si es el registro actual)
    is_current BOOLEAN NOT NULL DEFAULT TRUE,  -- Indica si el registro es el más reciente (activo)
    
    -- Clave compuesta
    CONSTRAINT payment_unique_key UNIQUE (payment_id, company_code, is_current)
);
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
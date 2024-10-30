CREATE TABLE "2024_pablo_estrada_schema".payments_l0 (
    id INTEGER IDENTITY(1,1) PRIMARY KEY,
    payment_id VARCHAR(50) NOT NULL,
    payment_at TIMESTAMP,
    company_code VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    external_client_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    start_date TIMESTAMP NOT NULL DEFAULT SYSDATE,
    end_date TIMESTAMP DEFAULT NULL,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,

    UNIQUE (payment_id, company_code, is_current)
);

CREATE TABLE "2024_pablo_estrada_schema".companies_l0 (
    id INTEGER IDENTITY(1,1) PRIMARY KEY,
    company_id VARCHAR(50) NOT NULL,
    company_code VARCHAR(50) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    category_id INTEGER,
    category_name VARCHAR(255),
    is_top_biller BOOLEAN DEFAULT FALSE
);
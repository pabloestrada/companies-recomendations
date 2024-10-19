SELECT t.payment_at, dc.company_id, t.amount, t.external_client_id, t2.id AS category_id,
       CASE
           WHEN tb.company_code IS NOT NULL THEN true
           ELSE false
       END AS is_top_biller
            FROM tapi_l2.fact_process_payments t
            join tapi_l2.dim_company dc on t.company_code = dc.company_code
            JOIN tapi_l1.companies_x_tags cxt ON dc.company_id = cxt.company_id
            JOIN tapi_l1.tags t2 ON t2.id = cxt.tag_id
            LEFT JOIN tapi_l1.top_billers tb ON tb.company_code = t.company_code
            WHERE t.company_code != 'AR-S-02283' and t.company_type = 'SERVICE' and t.country_code = 'AR' and t.external_client_id != '-'
            LIMIT 10
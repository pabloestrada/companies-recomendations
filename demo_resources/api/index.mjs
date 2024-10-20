// index.js
import express from "express";
import knexConfig from "./knexfile.mjs";
import knex from "knex";
import dotenv from "dotenv";

dotenv.config();

const db = knex(knexConfig.development);

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;

// Endpoint de ejemplo para obtener datos
app.get("/payments", async (req, res) => {
  try {
    const { updated_at, limit, offset } = req.query;

    // Verificar que se proporcione el parámetro updated_at
    if (!updated_at) {
      return res.status(400).json({
        error: "'updated_at' es requerido para filtrar los pagos.",
      });
    }

    let query = db("payments").select("*");

    // Filtrar por updated_at mayor al valor proporcionado
    query = query.where("updated_at", ">=", updated_at);

    // Aplicar limit y offset si están presentes
    if (limit) {
      query = query.limit(parseInt(limit));
    }

    if (offset) {
      query = query.offset(parseInt(offset));
    }

    // Ordenar por id
    query = query.orderBy("id");

    // Ejecutar la consulta
    const payments = await query;
    res.json(payments);
  } catch (error) {
    console.log("error:", error);
    res.status(500).json({ error: "Error fetching payments" });
  }
});

app.get("/companies", async (req, res) => {
  try {
    const { limit, offset } = req.query;
    let query = db("companies").select("*");

    // Aplicar limit y offset si están presentes
    if (limit) {
      query = query.limit(parseInt(limit));
    }

    if (offset) {
      query = query.offset(parseInt(offset));
    }

    // Ordenar por id
    query = query.orderBy("id");

    // Ejecutar la consulta
    const companies = await query;
    res.json(companies);
  } catch (error) {
    console.log("error:", error);
    res.status(500).json({ error: "Error fetching companies" });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

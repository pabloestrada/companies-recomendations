import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

// Esto obtiene la ruta completa del archivo actual en ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Construye la ruta absoluta desde el directorio actual donde está este archivo
const filePath = path.resolve(__dirname, "./companies_dataset.json");
console.log("Reading JSON file from:", filePath);

const data = JSON.parse(fs.readFileSync(filePath, "utf8"));

export const seed = async (knex) => {
  // Borrar los datos existentes en la tabla (opcional)
  await knex("companies").del();

  // Insertar los nuevos datos
  const batchSize = 1000;
  for (let i = 0; i < data.length; i += batchSize) {
    const batch = data.slice(i, i + batchSize);
    await knex("companies").insert(batch);
  }
};

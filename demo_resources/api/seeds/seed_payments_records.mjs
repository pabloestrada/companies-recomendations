import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import AdmZip from "adm-zip"; // Import adm-zip

// This gets the complete path of the current file in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths for the zip and the extracted JSON file
const zipFilePath = path.resolve(__dirname, "./payments_dataset.json.zip");
const jsonFilePath = path.resolve(__dirname, "./payments_dataset.json");

console.log("Extracting JSON file from zip:", zipFilePath);

// Unzip the JSON file using adm-zip
if (!fs.existsSync(jsonFilePath)) {
  try {
    const zip = new AdmZip(zipFilePath);
    zip.extractAllTo(__dirname, true); // Extract to the current directory
    console.log("Extraction complete, reading JSON file from:", jsonFilePath);
  } catch (error) {
    console.error("Error extracting ZIP file:", error);
  }
}

// Now read the JSON data
const data = JSON.parse(fs.readFileSync(jsonFilePath, "utf8"));

export const seed = async (knex) => {
  // Clear the existing data in the table (optional)
  await knex("payments").del();

  // Insert the new data in batches
  const batchSize = 1000;
  for (let i = 0; i < data.length; i += batchSize) {
    const batch = data.slice(i, i + batchSize);
    await knex("payments").insert(batch);
  }
};

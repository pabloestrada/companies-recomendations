// runSeed.js
import knexConfig from "../knexfile.mjs";
import knex from "knex";
import { seed as seedBillingRecords } from "./seed_payments_records.mjs"; // Ruta al archivo seed

import { seed as seedCompaniesRecords } from "./seed_companies_records.mjs"; // Ruta al archivo seed

const db = knex(knexConfig.migrations);

const runSeed = async () => {
  try {
    console.log("Running specific seed...");
    await seedBillingRecords(db); // Ejecuta la función seed
    console.log("Seed completed successfully");
  } catch (error) {
    console.error("Error running seed:", error);
  }

  try {
    console.log("Running specific seed...");
    await seedCompaniesRecords(db); // Ejecuta la función seed
    console.log("Seed completed successfully");
  } catch (error) {
    console.error("Error running seed:", error);
  }

  await db.destroy();
};

runSeed();

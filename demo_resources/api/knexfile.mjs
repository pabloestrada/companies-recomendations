import * as dotenv from "dotenv";
dotenv.config();

export default {
  development: {
    client: "pg",
    connection: {
      host: process.env.DB_HOST || "postgres",
      user: process.env.DB_USER || "api",
      password: process.env.DB_PASSWORD || "test",
      database: process.env.DB_NAME || "test_api_db",
      port: process.env.DB_PORT || 5432,
    },
    seeds: {
      directory: "./seeds",
    },
  },
  migrations: {
    client: "pg",
    connection: {
      host: process.env.DB_HOST || "postgres",
      user: process.env.DB_USER || "api",
      password: process.env.DB_PASSWORD || "test",
      database: process.env.DB_NAME || "test_api_db",
      port: process.env.DB_PORT || 5432,
    },
    seeds: {
      directory: "./seeds",
    },
  },
};

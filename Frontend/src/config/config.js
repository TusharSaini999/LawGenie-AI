// Centralized environment configuration
// Access env variables only through this file to avoid inconsistent access
// like `import.meta.env` failing in some modules.
const requiredEnv = ["VITE_API_BASE_URL"];

for (const key of requiredEnv) {
  if (!import.meta.env[key]) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
}

const config = Object.freeze({
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL,
  },
});
export default config;

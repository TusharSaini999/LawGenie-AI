// Centralized environment configuration
// Access env variables only through this file to avoid inconsistent access
// like `import.meta.env` failing in some modules.
const requiredEnv = ["VITE_API_BASE_URL"];

for (const key of requiredEnv) {
  // @ts-ignore
  if (!import.meta.env[key]) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
}

// @ts-ignore
const apiBaseUrlRaw = import.meta.env.VITE_API_BASE_URL?.trim();

if (!apiBaseUrlRaw || apiBaseUrlRaw === "...") {
  throw new Error(
    "Invalid VITE_API_BASE_URL. Set it to your backend URL, e.g. http://127.0.0.1:8000",
  );
}

try {
  // eslint-disable-next-line no-new
  new URL(apiBaseUrlRaw);
} catch {
  throw new Error(
    `Invalid VITE_API_BASE_URL format: ${apiBaseUrlRaw}. Use full URL format such as http://127.0.0.1:8000`,
  );
}

const config = Object.freeze({
  api: {
    baseUrl: apiBaseUrlRaw,
  },
});
export default config;

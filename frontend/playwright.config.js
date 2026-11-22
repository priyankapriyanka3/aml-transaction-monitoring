import { defineConfig } from '@playwright/test';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const E2E_BACKEND_PORT = process.env.E2E_BACKEND_PORT ?? '9000';
const E2E_FRONTEND_PORT = process.env.E2E_FRONTEND_PORT ?? '5173';
const E2E_PYTHON = process.env.E2E_PYTHON ?? 'python';
// Use a unique database file for each test run to avoid stale data
const E2E_DATABASE_URL = process.env.E2E_DATABASE_URL ?? `sqlite:///./_e2e_${Date.now()}.db`;
const E2E_TEST_TIMEOUT = Number(process.env.E2E_TEST_TIMEOUT ?? 30_000);
const E2E_ACTION_TIMEOUT = Number(process.env.E2E_ACTION_TIMEOUT ?? 10_000);
const E2E_NAVIGATION_TIMEOUT = Number(process.env.E2E_NAVIGATION_TIMEOUT ?? 15_000);
// Resolve backend directory relative to this config file
const backendDir = resolve(__dirname, '..', 'backend');
const venvPython = resolve(backendDir, '.venv', 'bin', 'python');
export default defineConfig({
    testDir: './e2e',
    timeout: E2E_TEST_TIMEOUT,
    retries: 0,
    workers: 1,
    reporter: [
        ['list'],
        ['junit', { outputFile: 'e2e-results/junit.xml' }],
    ],
    use: {
        baseURL: `http://127.0.0.1:${E2E_FRONTEND_PORT}`,
        actionTimeout: E2E_ACTION_TIMEOUT,
        navigationTimeout: E2E_NAVIGATION_TIMEOUT,
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
    },
    webServer: [
        {
            // Backend server with migrations and seed
            // Use venv python directly for consistent environment
            command: `cd ${backendDir} && ${venvPython} -m alembic upgrade head && ${venvPython} -m app.seed && ${venvPython} -m uvicorn app.main:app --host 127.0.0.1 --port ${E2E_BACKEND_PORT}`,
            port: Number(E2E_BACKEND_PORT),
            timeout: 180_000,
            reuseExistingServer: false,
            stdout: 'pipe',
            stderr: 'pipe',
            env: {
                DATABASE_URL: E2E_DATABASE_URL,
            },
        },
        {
            // Frontend dev server with backend proxy
            command: `npm run dev -- --host 127.0.0.1 --port ${E2E_FRONTEND_PORT} --strictPort`,
            port: Number(E2E_FRONTEND_PORT),
            timeout: 180_000,
            reuseExistingServer: false,
            stdout: 'pipe',
            stderr: 'pipe',
            env: {
                BACKEND_PORT: E2E_BACKEND_PORT,
            },
        },
    ],
});

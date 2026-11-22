import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig(({ mode }) => {
    // '' loads every variable, including the process environment start.sh sets
    const env = loadEnv(mode, process.cwd(), '');
    const backendPort = env.BACKEND_PORT || '9000';
    return {
        plugins: [react()],
        server: {
            port: 5173,
            strictPort: false,
            proxy: {
                // No rewrite: backend mounts routes under /api, path goes through unchanged
                '/api': {
                    target: `http://127.0.0.1:${backendPort}`,
                    changeOrigin: true,
                },
            },
        },
        preview: {
            port: 5173,
            strictPort: false,
        },
        test: {
            globals: true,
            environment: 'jsdom',
            setupFiles: './src/test/setup.ts',
            exclude: [
                '**/node_modules/**',
                '**/dist/**',
                '**/cypress/**',
                '**/.{idea,git,cache,output,temp}/**',
                '**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build}.config.*',
                '**/e2e/**', // Exclude Playwright E2E tests from vitest
                '**/tests/e2e/**',
            ],
        },
    };
});

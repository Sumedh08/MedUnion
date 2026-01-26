/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: {
                    primary: '#0a0f1a',
                    secondary: '#111827',
                    tertiary: '#1f2937',
                },
                risk: {
                    green: '#10b981',
                    amber: '#f59e0b',
                    red: '#ef4444',
                    critical: '#dc2626',
                },
                text: {
                    primary: '#f9fafb',
                    secondary: '#9ca3af',
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            }
        },
    },
    plugins: [],
}

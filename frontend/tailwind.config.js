/** @type {import('tailwindcss').Config} */
export default {
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
    theme: {
        extend: {
            colors: {
                chess: {
                    light: '#f0d9b5',
                    dark: '#b58863',
                    primary: '#769656',
                    secondary: '#eeeed2',
                },
            },
            fontFamily: {
                chess: ['Inter', 'system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [require('@tailwindcss/forms')],
}

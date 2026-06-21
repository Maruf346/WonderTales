/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./templates/**/*.html",
        "./apps/**/templates/**/*.html",
        "./static/**/*.js",
        // Ensure Unfold's internal templates are also considered for styling if you run a custom build
        "./.venv/lib/python*/site-packages/unfold/templates/**/*.html",
    ],
    theme: {
        extend: {},
    },
    plugins: [],
}

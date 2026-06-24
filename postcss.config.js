const purgecss = require('@fullhuman/postcss-purgecss')({
  content: [
    './templates/**/*.html',
    './**/*.py',
    './static/js/**/*.js',
  ],
  safelist: [
    /^btn/,
    /^modal/,
    /^dropdown/,
    /^show/,
    /^collapse/,
    /^fade/,
    /^active/,
  ]
});

module.exports = {
  plugins: [
    ...(process.env.NODE_ENV === 'production' ? [purgecss] : [])
  ]
}
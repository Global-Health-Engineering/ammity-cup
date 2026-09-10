import { defineConfig } from 'astro/config';

// Deployed as a GitHub Pages project site at
// https://global-health-engineering.github.io/ammity-cup, `base` MUST match
// the repo name or every absolute asset path (images, CSS, the brand SVG)
// 404s on the deployed site while working fine in local dev.
export default defineConfig({
  site: 'https://global-health-engineering.github.io',
  base: '/ammity-cup',
  build: { assets: '_astro' },
  vite: {
    build: {
      // three.js is ~590 kB raw (~150 kB gzipped) and trips Rollup's
      // default 500 kB warning. That warning exists to catch a large
      // chunk landing in the initial payload; this one cannot, because
      // src/scripts/model-viewer.js is reached only through a dynamic
      // import() fired by a click. Raised so a real regression in the
      // page's own bundle is not lost in an expected warning.
      chunkSizeWarningLimit: 700,
    },
  },
});

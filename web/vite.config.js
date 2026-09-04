import { defineConfig } from "vite";

// Project-site URL: https://dbraun1991.github.io/TriformFacet/ — hardcoded
// rather than derived from CI env, matching this repo's existing preference
// for no config layer beyond what it needs (ADR 0003).
export default defineConfig({
  base: "/TriformFacet/",
});

import type { Config } from "tailwindcss";
const config: Config = {
  content:["./src/pages/**/*.{js,ts,jsx,tsx,mdx}","./src/components/**/*.{js,ts,jsx,tsx,mdx}","./src/app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme:{extend:{colors:{background:"#f4f2e9",foreground:"#0b211b"},fontFamily:{sans:["Inter","ui-sans-serif","system-ui"],mono:["ui-monospace","SFMono-Regular","Menlo","monospace"]}}},
  plugins:[]
};
export default config;

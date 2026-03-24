export interface SiteConfig {
  title: string;
  description: string;
  url: string;
  author: string;
  authorDescription: string;
  social: {
    github: string;
    twitter: string;
    linkedin: string;
    email: string;
    bluesky: string;
    mastodon: string;
    leetcode: string;
    devto: string;
    lastfm: string;
  };
  giscus: {
    repo: string;
    repoId: string;
    category: string;
    categoryId: string;
    mapping: string;
    reactionsEnabled: string;
    emitMetadata: string;
    inputPosition: string;
    lang: string;
    loading: string;
    strict: string;
  };
  analytics: {
    cloudflareBeacon: string;
  };
  newsletter: {
    provider: "buttondown";
    username: string;
  };
  i18n: {
    defaultLocale: string;
    locales: string[];
  };
}

export const SITE_CONFIG: SiteConfig = {
  title: "Chirag Singhal",
  description:
    "Software Engineer specializing in scalable backend architectures, full-stack development, AI-driven automation, and cloud-native deployments.",
  url: "https://blog.oriz.in",
  author: "Chirag Singhal",
  authorDescription:
    "Software Engineer at TCS. Full Stack, Backend & Distributed Systems Specialist. JEE Advanced Rank Holder & College Topper (CGPA 8.81).",
  social: {
    github: "chirag127",
    twitter: "chirag127",
    linkedin: "chirag127",
    email: "hi@chirag127.in",
    bluesky: "chirag127.bsky.social",
    mastodon: "@chirag127@mastodon.social",
    leetcode: "chirag127",
    devto: "chirag127",
    lastfm: "lastfmwhy",
  },
  giscus: {
    repo: "chirag127/blog",
    repoId: "R_kgDORvXxEA",
    category: "General",
    categoryId: "DIC_kwDORvXxEM4C5Ka5",
    mapping: "pathname",
    reactionsEnabled: "1",
    emitMetadata: "0",
    inputPosition: "bottom",
    lang: "en",
    loading: "lazy",
    strict: "0",
  },
  analytics: {
    cloudflareBeacon: "", // Set via PUBLIC_CF_BEACON env var
  },
  newsletter: {
    provider: "buttondown",
    username: "chirag127",
  },
  i18n: {
    defaultLocale: "en",
    locales: ["en", "hi"],
  },
};

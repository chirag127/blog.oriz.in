/// <reference types="astro/client" />

declare module "astro:content" {
  interface ContentConfig {
    collections: {
      blog: {
        schema: import("astro/zod").AnyZodObject;
      };
    };
  }
}

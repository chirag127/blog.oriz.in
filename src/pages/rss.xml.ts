import rss from "@astrojs/rss";
import { getCollection, type CollectionEntry } from "astro:content";
import type { APIContext } from "astro";
import { SITE_CONFIG } from "../config";

export async function GET(context: APIContext) {
  const posts = await getCollection("blog", (entry: CollectionEntry<"blog">) => !entry.data.draft);
  const sortedPosts = posts.sort(
    (a: CollectionEntry<"blog">, b: CollectionEntry<"blog">) =>
      b.data.pubDate.valueOf() - a.data.pubDate.valueOf(),
  );

  return rss({
    title: SITE_CONFIG.title,
    description: SITE_CONFIG.description,
    site: context.site?.toString() || SITE_CONFIG.url,
    items: sortedPosts.map((post: CollectionEntry<"blog">) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      link: `/blog/${post.id}/`,
    })),
    customData: `<language>en-us</language>`,
  });
}

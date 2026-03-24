import type { APIContext } from "astro";
import { getCollection, type CollectionEntry } from "astro:content";

export async function GET(_context: APIContext) {
  const posts = await getCollection("blog", (entry: CollectionEntry<"blog">) => !entry.data.draft);
  const sortedPosts = posts.sort(
    (a: CollectionEntry<"blog">, b: CollectionEntry<"blog">) =>
      b.data.pubDate.valueOf() - a.data.pubDate.valueOf(),
  );

  const searchIndex = sortedPosts.map((post: CollectionEntry<"blog">) => ({
    id: post.id,
    title: post.data.title,
    description: post.data.description,
    tags: post.data.tags,
    category: post.data.category,
    url: `/blog/${post.id}/`,
    date: post.data.pubDate.toISOString(),
  }));

  return new Response(JSON.stringify(searchIndex), {
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "public, max-age=3600",
    },
  });
}

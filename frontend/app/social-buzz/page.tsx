import Link from "next/link";

import { fetchSocialBuzz } from "@/lib/api";

export default async function SocialBuzzPage() {
  const posts = await fetchSocialBuzz("healthcare ai llm", 30);

  return (
    <main className="min-h-screen px-6 py-8">
      <section className="mx-auto w-full max-w-6xl">
        <header className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h1 className="text-3xl font-semibold text-slate-900">Social Buzz</h1>
          <p className="mt-2 text-sm text-slate-600">Latest X discussions around healthcare AI and frontier AI.</p>
        </header>

        <section className="mt-6 space-y-3">
          {posts.length === 0 ? <p className="text-sm text-slate-600">No social buzz available.</p> : null}
          {posts.map((post) => (
            <article key={post.id} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-800">{post.text}</p>
              <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
                <span className="rounded-full bg-slate-100 px-2 py-1">@{post.author}</span>
                <span className="rounded-full bg-slate-100 px-2 py-1">Likes {post.public_metrics.like_count}</span>
                <span className="rounded-full bg-slate-100 px-2 py-1">Retweets {post.public_metrics.retweet_count}</span>
                <span className="rounded-full bg-slate-100 px-2 py-1">Replies {post.public_metrics.reply_count}</span>
                <span className="rounded-full bg-emerald-100 px-2 py-1 text-emerald-700">{post.primary_topic}</span>
                {post.topic_tags.slice(0, 3).map((tag) => (
                  <span key={`${post.id}-${tag}`} className="rounded-full bg-blue-100 px-2 py-1 text-blue-700">
                    {tag}
                  </span>
                ))}
              </div>
              <div className="mt-3">
                <Link href={post.post_url} target="_blank" className="text-sm font-medium text-slate-700 underline">
                  Open on X
                </Link>
              </div>
            </article>
          ))}
        </section>
      </section>
    </main>
  );
}

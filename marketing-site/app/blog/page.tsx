import { getAllPosts } from "@/lib/blog";

export default function BlogIndexPage() {
  const posts = getAllPosts();

  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-bold tracking-tight mb-10">Blog</h1>

      {posts.length === 0 && (
        <p className="text-slate-500">Nothing published yet — check back soon.</p>
      )}

      <div className="flex flex-col gap-6">
        {posts.map((post) => (
          <a
            key={post.slug}
            href={`/blog/${post.slug}`}
            className="block rounded-xl border border-slate-200 bg-white p-6 hover:border-slate-400 hover:shadow-sm transition-all"
          >
            <p className="text-xs text-slate-500 mb-1">{post.date}</p>
            <h2 className="font-semibold text-lg text-slate-900 mb-1">
              {post.title}
            </h2>
            <p className="text-slate-600 text-sm">{post.description}</p>
          </a>
        ))}
      </div>
    </div>
  );
}

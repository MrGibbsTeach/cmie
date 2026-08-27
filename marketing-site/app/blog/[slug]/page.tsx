import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { getAllPosts, getPost } from "@/lib/blog";

export async function generateStaticParams() {
  return getAllPosts().map((post) => ({ slug: post.slug }));
}

export default async function BlogPostPage(props: PageProps<"/blog/[slug]">) {
  const { slug } = await props.params;
  const post = getPost(slug);
  if (!post) notFound();

  return (
    <article className="max-w-2xl mx-auto px-6 py-16">
      <p className="text-xs text-slate-500 mb-2">{post.date}</p>
      <h1 className="text-3xl font-bold tracking-tight mb-8">{post.title}</h1>
      <div className="prose prose-slate max-w-none">
        <ReactMarkdown>{post.content}</ReactMarkdown>
      </div>
    </article>
  );
}

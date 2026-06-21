import type { BlogPost } from '../types/blog'
import { Link } from 'react-router-dom'

interface BlogCardProps {
  post: BlogPost
}

export default function BlogCard({ post }: BlogCardProps) {
  return (
    <article className="group">
      <div className="overflow-hidden rounded-2xl">
        <img
          src={post.image}
          alt={post.title}
          className="aspect-[4/3] w-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
      </div>
      <h2 className="mt-4 text-base font-semibold text-white leading-snug">
        {post.title}
      </h2>
      <Link
        to={`/blog/${post.slug}`}
        className="mt-3 inline-flex items-center gap-1 text-sm text-gold font-medium hover:underline"
      >
        Read more <span className="text-xs">›</span>
      </Link>
    </article>
  )
}

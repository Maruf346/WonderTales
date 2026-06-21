import { useEffect } from 'react'
import BlogCard from '../components/BlogCard'
import { useBlogStore } from '../cotexts/blogStore'

export default function BlogsPage() {
  const { blogs, fetchBlogs, loading } = useBlogStore()

  useEffect(() => {
    window.scrollTo(0, 0)
    fetchBlogs()
  }, [fetchBlogs])

  return (
    <div className="bg-navy-950 px-6 py-16 lg:px-8 min-h-[60vh]">
      <div className="mx-auto max-w-7xl">
        <h1 className="font-serif text-4xl text-white sm:text-5xl">
          <span className="text-gold">Blogs</span> for Children
        </h1>

        {loading && blogs.length === 0 ? (
          <div className="mt-20 text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-gold border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" />
            <p className="mt-4 text-slate-400">Loading magic stories...</p>
          </div>
        ) : (
          <div className="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {blogs.map((post) => (
              <BlogCard key={post.slug} post={post} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

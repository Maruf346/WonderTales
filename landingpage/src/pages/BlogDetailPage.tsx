import { useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useBlogStore } from '../cotexts/blogStore'

export default function BlogDetailPage() {
  const { slug } = useParams()
  const { activeBlog, fetchBlogBySlug, loading } = useBlogStore()

  useEffect(() => {
    window.scrollTo(0, 0)
    if (slug) {
      fetchBlogBySlug(slug)
    }
  }, [slug, fetchBlogBySlug])

  // Dynamic SEO Injection
  useEffect(() => {
    if (activeBlog) {
      // Set Document Title
      document.title = activeBlog.meta_title || activeBlog.title

      // Set Meta Description
      let metaDesc = document.querySelector('meta[name="description"]')
      if (!metaDesc) {
        metaDesc = document.createElement('meta')
        metaDesc.setAttribute('name', 'description')
        document.head.appendChild(metaDesc)
      }
      metaDesc.setAttribute('content', activeBlog.meta_description || activeBlog.excerpt || '')

      // Set Meta Keywords
      let metaKeywords = document.querySelector('meta[name="keywords"]')
      if (!metaKeywords) {
        metaKeywords = document.createElement('meta')
        metaKeywords.setAttribute('name', 'keywords')
        document.head.appendChild(metaKeywords)
      }
      metaKeywords.setAttribute('content', activeBlog.meta_keywords || '')
    }

    return () => {
      // Restore default title on unmount
      document.title = 'WonderTales'
    }
  }, [activeBlog])

  if (loading) {
    return (
      <div className="min-h-[60vh] bg-navy-950 px-6 py-20 text-center flex flex-col justify-center items-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-gold border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" />
        <p className="mt-4 text-slate-400">Unveiling story details...</p>
      </div>
    )
  }

  if (!activeBlog) {
    return (
      <div className="min-h-[60vh] bg-navy-950 px-6 py-20 text-center text-slate-300 lg:px-8">
        <h2 className="font-serif text-3xl text-white">Blog not found</h2>
        <p className="mt-4 text-sm text-slate-400">The story you're looking for is not available yet.</p>
        <Link to="/blogs" className="mt-6 inline-block text-gold hover:underline">
          &larr; Back to all blogs
        </Link>
      </div>
    )
  }



  return (
    <div className="bg-navy-950 px-6 py-16 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <Link to="/blogs" className="text-gold hover:underline text-sm font-medium flex items-center gap-2 mb-8">
          &larr; Back to Blogs
        </Link>

        <h1 className="font-serif text-3xl text-gold sm:text-4xl leading-snug">
          {activeBlog.title}
        </h1>

        <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-xs text-slate-400 items-center">
          <span>By <strong className="text-white">{activeBlog.author || 'WonderTales Hub'}</strong></span>
          <span className="h-1 w-1 rounded-full bg-slate-600" />
          <span>{activeBlog.date || 'Recently'}</span>
        </div>

        {activeBlog.image && (
          <img
            src={activeBlog.image}
            alt={activeBlog.title}
            className="mt-8 w-full max-w-2xl rounded-2xl object-cover aspect-video shadow-2xl"
          />
        )}

        <div 
          className="mt-10 prose prose-invert prose-gold max-w-none text-slate-300"
          dangerouslySetInnerHTML={{ __html: activeBlog.content || '' }}
        />

        {activeBlog.tags_list && activeBlog.tags_list.length > 0 && (
          <div className="mt-12 pt-8 border-t border-slate-800">
            <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-3">Tags</h4>
            <div className="flex flex-wrap gap-2">
              {activeBlog.tags_list.map((tag) => (
                <span key={tag} className="text-xs px-3 py-1.5 rounded-full bg-navy-900 border border-slate-800 text-gold">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

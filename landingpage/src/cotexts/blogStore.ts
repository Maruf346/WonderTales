import { create } from 'zustand'
import type { BlogPost } from '../types/blog'

interface BlogState {
  blogs: BlogPost[]
  activeBlog: BlogPost | null
  loading: boolean
  error: string | null
  fetchBlogs: () => Promise<void>
  fetchBlogBySlug: (slug: string) => Promise<BlogPost | null>
  getBlogBySlug: (slug: string) => BlogPost | undefined
}

const coverBedtime = new URL('../assets/dreamina-2026-05-16-1502 2.png', import.meta.url).href
const coverDreamWeaver = new URL('../assets/ChatGPT Image May 16, 2026, 03_20_34 PM 1.png', import.meta.url).href
const coverNightTales = new URL('../assets/Gemini_Generated_Image_tzaukstzaukstzau 1.png', import.meta.url).href

const mockBlogs: BlogPost[] = [
  {
    slug: 'storytelling-bedtime',
    title: 'The Art of Storytelling: How to Read Bedtime Stories',
    excerpt: 'Turn the bedtime routine into a calm ritual with cozy pacing, warm voice, and simple storytelling tricks.',
    category: 'Parenting',
    date: 'May 16, 2026',
    image: coverBedtime,
    content:
      'There is a distinct kind of magic that settles over a home at the end of the day. The frantic energy of school, work, and play begins to fade, replaced by the soft glow of a bedside lamp and the quiet rustle of turning pages.\nReading a bedtime story isn\'t just a checklist item before turning off the lights—it is an art form. Done right, it bridges the gap between a hectic day and a peaceful night\'s sleep, building a sanctuary of warmth, imagination, and security for your child.\nHere is how you can master the art of the bedtime story and turn a simple routine into an unforgettable nightly ritual.\n\n1. Set the Stage\n\nBefore you even open the cover, you need to cultivate the right environment. The transition from the high stimulation of evening activities to a sleep-ready state requires sensory cues.\n\n• Dim the Lights: Switch off harsh overhead lighting. Use a warm bedside lamp or a reading light just bright enough to see the text.\n• Get Cozy: Ensure the physical space is comfortable. Pile up pillows, pull up the blankets, and sit close enough that your child can feel your presence and easily view the illustrations.\n• Leave Electronics Outside: The bedroom should be a screen-free zone during this time. No notification pings, no scrolling—just the two of you and the book.\n\n2. Master Your Delivery\n\nRead slowly and intentionally. Let each sentence breathe. Use gentle inflections and pauses at key moments, and lean into the emotional beats of the story. This helps your child tune in, follow the plot, and feel the rhythm of the narrative.\n\n3. Create Connection\n\nAsk simple questions as you go: "What do you think will happen next?" or "How does this character feel?" This keeps your child engaged while strengthening their imagination and making the story feel personal.\n\nThe Ultimate Benefit\n\nA bedtime story done with care does more than entertain. It creates a nightly ritual that builds trust, deepens connection, and nurtures a love of reading that can last a lifetime.',
  },
  {
    slug: 'dream-weaver-guide',
    title: 'Dream Weaver\'s Guide: Crafting Magical Bedtime Stories',
    excerpt: 'Learn how to shape characters, set a gentle tone, and keep adventures calm enough for sleepy imaginations.',
    category: 'Storytelling',
    date: 'May 14, 2026',
    image: coverDreamWeaver,
    content:
      'Discover how to craft bedtime stories that feel enchanted yet soothing. The Dream Weaver\'s Guide helps parents balance wonder with rest, keeping every tale simple, kind, and easy to follow.',
  },
  {
    slug: 'enchanting-night-tales',
    title: 'Enchanting Night Tales: Unleash Your Child\'s Imagination',
    excerpt: 'Create stories that spark curiosity and comfort with gentle heroes, warm worlds, and a calm ending every night.',
    category: 'Imagination',
    date: 'May 12, 2026',
    image: coverNightTales,
    content:
      'Bedtime stories that invite your child into a soft, imaginative world can make the difference between restless nights and restful sleep. Use familiar themes, kind characters, and clear story arcs to keep every adventure bright and reassuring.',
  },
]

const getApiBase = () => {
  const hostname = typeof window !== 'undefined' ? window.location.hostname : '';
  
  // If we are running on localhost, use the env var or default to localhost:8000
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '') {
    return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  }
  
  // If we are in production, use the production API domain
  if (hostname.includes('wondertaleshub.com')) {
    return 'https://api.wondertaleshub.com';
  }
  
  // Dynamic fallback for any other production domains
  return `https://api.${hostname}`;
};

const API_BASE = getApiBase();

export const useBlogStore = create<BlogState>((set, get) => ({
  blogs: mockBlogs,
  activeBlog: null,
  loading: false,
  error: null,

  fetchBlogs: async () => {
    set({ loading: true, error: null })
    try {
      const res = await fetch(`${API_BASE}/v1/blogs/`)
      if (!res.ok) throw new Error('Failed to fetch blogs')
      const data = await res.json()
      if (data) {
        const mapped = data.map((b: any) => ({
          ...b,
          excerpt: b.content ? b.content.substring(0, 120) + '...' : b.excerpt || '',
          category: b.tags_list && b.tags_list.length > 0 ? b.tags_list[0] : 'Parenting',
          date: b.updated_at ? new Date(b.updated_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          }) : 'Recently',
          image: b.image ? (b.image.startsWith('http') ? b.image : `${API_BASE}${b.image}`) : coverBedtime,
        }))
        set({ blogs: mapped, loading: false })
      } else {
        set({ blogs: [], loading: false })
      }
    } catch (err: any) {
      console.warn('API fetch failed, falling back to mock blogs:', err.message)
      set({ loading: false })
    }
  },

  fetchBlogBySlug: async (slug: string) => {
    set({ loading: true, error: null })
    try {
      const res = await fetch(`${API_BASE}/v1/blogs/${slug}/`)
      if (!res.ok) throw new Error('Blog post not found')
      const data = await res.json()
      const mapped = {
        ...data,
        excerpt: data.content ? data.content.substring(0, 120) + '...' : data.excerpt || '',
        category: data.tags_list && data.tags_list.length > 0 ? data.tags_list[0] : 'Parenting',
        date: data.updated_at ? new Date(data.updated_at).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        }) : 'Recently',
        image: data.image ? (data.image.startsWith('http') ? data.image : `${API_BASE}${data.image}`) : coverBedtime,
      }
      set({ activeBlog: mapped, loading: false })
      return mapped
    } catch (err: any) {
      // Fallback to mock blogs
      const mockFound = mockBlogs.find((item) => item.slug === slug)
      if (mockFound) {
        set({ activeBlog: mockFound, loading: false })
        return mockFound
      }
      set({ loading: false, error: err.message })
      return null
    }
  },

  getBlogBySlug: (slug: string) => {
    return get().blogs.find((item) => item.slug === slug)
  },
}))

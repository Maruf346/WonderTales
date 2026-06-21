export interface BlogPost {
  id?: number
  slug: string
  title: string
  content?: string
  author?: string
  excerpt?: string
  category?: string
  date?: string
  image?: string
  tags_list?: string[]
  created_at?: string
  updated_at?: string
  meta_title?: string
  meta_description?: string
  meta_keywords?: string
}

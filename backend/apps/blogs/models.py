from django.db import models
from django.utils.text import slugify

class BlogModel(models.Model):
    """
    Stores blog posts with custom SEO-friendly metadata and tags for search engine optimization.
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="Used in SEO-friendly URL paths. Automatically generated if left blank.")
    author = models.CharField(max_length=100, default="WonderTales Hub")
    content = models.TextField()
    image = models.ImageField(upload_to='blogs/images/', blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated list of tags.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # SEO Meta Fields
    meta_title = models.CharField(max_length=255, blank=True, null=True, help_text="SEO Title tag fallback (optional).")
    meta_description = models.TextField(blank=True, null=True, help_text="SEO Meta Description.")
    meta_keywords = models.CharField(max_length=255, blank=True, null=True, help_text="SEO Meta Keywords.")

    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

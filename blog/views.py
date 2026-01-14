from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost, BlogCategory


def blog_list(request):
    """Blog list page with pagination and filtering"""
    posts = BlogPost.objects.filter(status='published').select_related('author', 'category')
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(meta_keywords__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Pagination
    paginator = Paginator(posts, 12)  # 12 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for filter
    categories = BlogCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug,
    }
    
    return render(request, 'blog/blog_list.html', context)


def blog_detail(request, slug):
    """Blog detail page with related posts"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Increment view count
    post.view_count += 1
    post.save(update_fields=['view_count'])
    
    # Get related posts (same category, exclude current)
    related_posts = BlogPost.objects.filter(
        status='published',
        category=post.category
    ).exclude(id=post.id)[:3]
    
    # Generate table of contents from H2 and H3 tags
    import re
    headings = re.findall(r'<h([23])>(.*?)</h\1>', post.content)
    toc = [{'level': int(level), 'text': text} for level, text in headings]
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'toc': toc,
    }
    
    return render(request, 'blog/blog_detail.html', context)

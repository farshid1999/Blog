from blog.models import *
from django import template
from django.db.models import Count
from markdown import markdown
from django.utils.safestring import mark_safe



register=template.Library()

@register.simple_tag()
def total_posts():
    return Post.status_state.published().count()

@register.simple_tag()
def total_comment():
    return Comment.objects.count()

@register.simple_tag()
def last_post_date():
    return Post.status_state.published().last()

@register.inclusion_tag('partials/latest_posts.html')
def latest_posts(count=3):
    lp=Post.status_state.published().order_by('-publish')[:count]
    coutext={'Lp':lp}
    return coutext

@register.simple_tag()
def most_popular_post(count=3):
    return Post.status_state.published().annotate(popular_comment_count=Count('comment')).order_by('-popular_comment_count')[:count]

@register.filter(name='markdown')
def to_markdown(text):
    return mark_safe(markdown(text))

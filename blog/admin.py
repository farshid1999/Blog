from django.contrib import admin
from .models import *
from django_jalali.admin.filters import JDateFieldListFilter
import django_jalali.admin as jadmin
# Register your models here.


admin.sites.AdminSite.site_header="پنل مدیریت جنگو"
admin.sites.AdminSite.site_title="پنل مدیریت"
admin.sites.AdminSite.index_title="پنل ادمین اپلیکیشن بلاگ"


class ImageInline(admin.StackedInline):
    model = Image
    extra = 1
    readonly_fields = ['title']
class CommentInline(admin.TabularInline):
    model = Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author','title','publish','status','comment_count']
    ordering = ('title','-publish')
    list_filter = ('status','author',('publish',JDateFieldListFilter))
    search_fields = ('title','description')
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    # prepopulated_fields = {'slug':('title',)}
    inlines = [ImageInline]

    def comment_count(self,obj):
        return obj.comment.count()

    comment_count.short_description = 'تعداد کامنت ها'

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['name','message','subject','phone','email']


@admin.register(Comment)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['post','name','created','active']
    list_filter = ['active',('created',JDateFieldListFilter)]
    search_fields = ['name','body']
    list_editable = ['active']

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['post','title','created']

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user','birthdate']
    list_filter = ('user',('birthdate',JDateFieldListFilter),'user__is_active')
    search_fields = ['user__is_active','user__last_name','user__first_name','user__email']


from django.contrib.auth.decorators import login_required
from django.contrib.postgres.lookups import TrigramSimilar
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.views import View
from unicodedata import category

from .models import Post
import datetime
from django.core.paginator import Paginator
from django.views.generic.list import ListView
from .forms import *
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.db.models.query import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from blog.apps import BlogConfig
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.hashers import

# blog_config = apps.get_app_config('blog')



# Create your views here.

def register(request):
    if request.method == "POST":
        form = RegisterPost(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(email=email).exists():
                return HttpResponse("Email already registered")
            if User.objects.filter(username=username).exists():
                return HttpResponse("Username is already taken")

            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_active = False
            user.save()
            # TODO: send email
            return redirect('profile')
    else:
        form = RegisterPost()
    return render(request, 'forms/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('post_list_page')
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('profile')
                else:
                    return HttpResponse('your account is not activate')
            else:
                return redirect('login')
        else:
            return HttpResponse('username or passsword is not available')
    else:
        form = LoginForm()
        return render(request,'forms/login.html',{'form':form})

def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')




def post_list(request):
    published_posts = Post.status_state.published().all()
    paginator = Paginator(published_posts, 2)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)
    context = {
        'posts': posts,
        # 'category': category
    }
    return render(request, 'blog/post_list.html', context=context)


def post_detail(request, slug):
    try:
        post = Post.status_state.published().get(slug=slug)
    except:
        raise Http404("NOT FOUND")
    context = {
        'post': post
    }
    return render(request, 'blog/post_detail.html', context=context)


def ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_page')
    form = TicketForm()
    return render(request, 'forms/ticket.html', {'form': form})


@require_POST
def post_comment(request, id):
    post = get_object_or_404(Post, id=id, status=Post.Status.PUBLISHED)

    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    context = {'post': post, 'form': form, 'comment': comment}
    return render(request, 'forms/comment.html', context)

@login_required
def index(request):
    return render(request, 'blog/index.html')

@login_required
def creatpost(request):
    if request.method == "GET":
        post_form = PostModelForm()
        context = {
            'form': post_form,
        }
        return render(request, 'forms/create_post.html', context)

    if request.method == "POST":
        post_form = PostModelForm(request.POST)
        if post_form.is_valid():
            title = post_form.cleaned_data['title']
            description = post_form.cleaned_data['description']
            reading_time = post_form.cleaned_data['reading_time']
            published_post = Post.objects.filter(title=title, status=Post.Status.PUBLISHED).first()

            if not published_post:
                current_post=Post.objects.create(
                    title=title,
                    description=description,
                    reading_time=reading_time,
                    status=Post.Status.DRAFT,
                    author=request.user
                )
                for key , uploaded_file in request.FILES.items():
                    Image.objects.create(
                        title=title,
                        post=current_post,
                        image_file=uploaded_file,
                    )

                return redirect('post_list_page')

            else:
                return redirect('creat_post')

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect('profile')


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = PostModelForm(request.POST,instance=post)

        if form.is_valid():
            form.save(commit=False)
            post.author=request.user
            post.status=Post.Status.DRAFT
            post.save()
            return redirect('profile')
        return redirect('edit_post', id=post_id)
    else:
        form = PostModelForm(instance=post)
        images = Image.objects.filter(post=post)
        return render(request,'blog/edit_post.html',{'form':form, 'images':images})


def post_search(request):
    query = None
    result = []
    if 'query' in request.GET:
        form = SearchPost(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # result = Post.status_state.published().filter(Q(description__icontains=query)|Q(title__icontains=query))
            # result = Post.status_state.published().filter(Q(title__search=query) | Q(description__search=query)).all()
            # result = Post.status_state.published().annotate(search=SearchVector('description','title')).filter(search=query)

            # search_query = SearchQuery(query)
            # search_vector=SearchVector('description',weight='B')+SearchVector('title',weight='A')
            # result = Post.status_state.published().annotate(search=search_vector,rank=SearchRank(search_vector,search_query)).filter(
            #     search=search_query).order_by('-rank')

            result = Post.status_state.published().annotate(similarity=TrigramSimilar('title',query)).filter(similarity__gte=0.1).order_by('-similarity')
            context = {
                'form': form,
                'query': query,
                'result': result
            }
            return render(request, 'blog/search.html', context)

@login_required
def profile(request):
    user = request.user
    posts = Post.status_state.published().filter(author=user)
    context = {
        'posts': posts,
        'user': user
    }
    return render(request, 'blog/profile.html', context)

def register(request):
    if request.method == "POST":
        form=UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Account.objects.create(user=user)
            return redirect('login')
    else:
        form=UserRegisterForm()
        return render(request, 'registration/user_registration.html', context={'form':form})

@login_required
def edit_account(request):
    user_form = UserEditForm(request.POST,instance=request.user)
    account_form = UserEditForm(request.POST,instance=request.user.account,files=request.FILES)
    if user_form.is_valid() and account_form.is_valid():
        account_form.save()
        user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        account_form = UserEditForm(instance=request.user.account)
        context = {
            'user_form': user_form,
            'account_form': account_form,
        }
        return render(request,'registration/edit_account.html',context)

def author(request,id):
    current_author=Post.status_state.published().filter(author_id=id).first()
    posts = Post.status_state.published().filter(author=current_author).order_by('-reading_time').all()

    return render(request,'blog/post_by_author.html',{'posts':posts,'author':current_author})
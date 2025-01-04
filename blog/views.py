import base64
import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ArticleForm,ArticleMediaForm, CommentsForm
from .models import Article,ArticleMedia,Tags,Comments
from authentication.models import User
from .utils import parse_content
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.http import Http404, HttpResponse

@login_required(login_url="login")
def index(request):
    # if not request.user.is_authenticated:
    #     return redirect('login')

    context = {
        'articles': Article.objects.all(),
        'user': request.user,
        'tags': Tags.objects.all(),
    }

    return render(request,'blog/index.html',context)

@login_required(login_url="login")
def post(request):
    context = {
        'form1': ArticleForm(),
        'form2': ArticleMediaForm(),
        'tags': Tags.objects.all()[:15],

    }
    if request.method == "POST":
        form1 = ArticleForm(request.POST)
        form2 = ArticleMediaForm(request.POST,request.FILES)
        if form1.is_valid() and form2.is_valid(): 
            article = form1.save(commit=False)
            content, extracted_images_urls = parse_content(article.content)
            article.content = content
            article.author = request.user
            article.save()

            form1.save_m2m()

            image_url_map = {}
            for index,image_url in enumerate(extracted_images_urls):
                header, base64_str = image_url.split(",",1)
                image_data = base64.b64decode(base64_str)
                format_str = header.split(";")[0].split("/")[1]
                image_name = f"{article.title}_{article.author}_detail_{index}.{format_str}"
                image_file = ContentFile(image_data,image_name)

                media = ArticleMedia(
                    article = article,
                    image = image_file,
                    filename = image_file.name,
                    size = image_file.size,
                    type = "DETAIL",
                )
                media.save()

                image_url_map[index] = media.image.url

            for index, url in image_url_map.items():
                content = content.replace(f'src="{index}"', f'src="{url}"')

            article.content = content
            article.save()

            image = form2.save(commit=False)
            image.article = article
            image.filename = image.image.name
            image.size = image.image.size
            image.save()
            return redirect('index')
        context['form1'] = form1
        context['form2'] = form2

    return render(request,'blog/post.html',context)

@login_required(login_url="login")
def update(request,article_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        article = Article.objects.get(id = article_id)
    except:
        return render(request, 'blog/update.html', context={'error': 'Article does not exist'})
    media = ArticleMedia.objects.get(article = article, type="BANNER") # Assuming all articles have a banner image
    
    form1 = ArticleForm(instance = article)
    form2 = ArticleMediaForm(instance = media)

    if request.method == "POST":
        form1 = ArticleForm(request.POST, instance=article)
        form2 = ArticleMediaForm(request.POST, request.FILES, instance=media)

        if form1.is_valid() and form2.is_valid():
            medias = ArticleMedia.objects.filter(article = article)
            for media in medias:
                media.delete()

            updated_article = form1.save()

            if hasattr(form1, 'save_m2m'):
                form1.save_m2m()

            updated_content, extracted_image_urls = parse_content(updated_article.content)
            image_url_map = {}
            for index, image_url in enumerate(extracted_image_urls):
                if 'media' in image_url:
                    desired_url = os.path.normpath(image_url).replace(".." + os.sep,"")
                    image_url_map[index] = desired_url if desired_url.startswith('/media') else '/' + desired_url
                    continue

                header, base64_str = image_url.split(",",1)
                image_data = base64.b64decode(base64_str)
                format_str = header.split(";")[0].split("/")[1]
                image_name = f"{article.title}_{article.author}_detail_{index}.{format_str}"
                image_file = ContentFile(image_data,image_name)

                media = ArticleMedia(
                    article = article,
                    image = image_file,
                    filename = image_file.name,
                    size = image_file.size,
                    type = "DETAIL",
                )
                media.save()

                image_url_map[index] = media.image.url

            for index, url in image_url_map.items():
                updated_content = updated_content.replace(f'src="{index}"',f'src="{url}"')
            updated_article.content = updated_content
            updated_article.save()

            banner_image = form2.save(commit=False)
            banner_image.article = updated_article
            banner_image.save()
            messages.success(request,"Updated Article Successfully!")

            return redirect('profile')

    context = {
        'article': article,
        'tags': Tags.objects.all()[:15],
        'form1': form1,
        'form2': form2,
    }

    return render(request, 'blog/update.html', context)

@login_required(login_url="login")
def details(request,article_id):
    article = Article.objects.get(id = article_id)
    comments_form = CommentsForm()

    comments = Comments.objects.filter(article__id = article_id, parent = None)
    paginator = Paginator(comments, per_page=5)
    page_obj = paginator.get_page(request.GET.get('page'))

    if request.headers.get('Hx-Request'):
        return render(request, "blog/extra_comments.html", {"article": article, "comments": page_obj, "comments_form": comments_form})

    context = {
        'article': article,
        'image': ArticleMedia.objects.get(article__id = article_id,type="BANNER"),
        'tags': Tags.objects.all()[:15],
        'related_articles': Article.objects.filter(tags = article.tags.order_by("?").first()).exclude(id = article_id)[:5],
        'comments_form': comments_form,
        'comments': page_obj,
        'true_user': request.user,        
    }
    return render(request, 'blog/details.html', context)

def profile(request, username):
    # user = request.user
    user = User.objects.get(username = username)

    context = {
        'user': user,
        'articles': Article.objects.filter(author = user),
        'tags': Tags.objects.all()[:15],    
    }

    if user == request.user: #The current user
        context['logged_in'] = True
    else:
        context['true_user'] = request.user
    return render(request,'blog/profile.html',context)

def delete(request, article_id):
    article = get_object_or_404(Article,id=article_id)
    media = ArticleMedia.objects.filter(article = article)
    for m in media: m.delete();
    article.delete()
    user = request.user
    context = {
        'user': user,
        'articles': Article.objects.filter(author = user),
    }
    return render(request, 'blog/profile.html',context)

def list(request, tag_name:str = None):
    if not request.user.is_authenticated:
        return redirect('login')

    if tag_name == None:
        articles = Article.objects.all()
    else:
        articles = Article.objects.filter(tags__name = tag_name)
        if 'tag_shown' not in request.session:
            messages.success(request,f'Showing {tag_name} articles')
            request.session['tag_shown'] = tag_name
        elif request.session['tag_shown'] != tag_name:
            messages.success(request,f'Showing {tag_name} articles')
            request.session['tag_shown'] = tag_name

    paginator = Paginator(articles, per_page=9)
    page_obj = paginator.get_page(request.GET.get('page'))

    if request.headers.get('HX-Request'):
        return render(request, 'blog/article_list.html', {'page_obj': page_obj})

    context = {
        'page_obj': page_obj,
        'tags': Tags.objects.all(),
    }
    return render(request, 'blog/list.html', context)
    
def search(request):
    if request.method == "GET":
        name = request.GET.get('name').strip() if request.GET.get('name') else None
        tag = request.GET.get('tag').strip() if request.GET.get('tag') else None

        query = Q()
        search_query = []

        if name is not None:
            query &= Q(title__contains = name)
            search_query.append(name)

        if tag is not None:
            query &= Q(tags__name__contains = tag)
            search_query.append(tag)

        articles = Article.objects.filter(query)
        paginator = Paginator(articles, per_page=9)
        page_obj = paginator.get_page(request.GET.get('page'))

        if request.headers.get('HX-Request'):
            return render(request, 'blog/article_list.html', {'page_obj': page_obj})
        
        messages.success(request, f"Search results for: {' and '.join(search_query)}")
        context = {
            'page_obj': page_obj,
            'tags': Tags.objects.all(),
        }

        return render(request, 'blog/list.html', context)

    return Http404("Something went wrong here! You are not supposed to be here")

def comment(request, article_id):
    if request.method == 'POST':
        comments_form = CommentsForm(request.POST)
        if comments_form.is_valid():
            comment = comments_form.save(commit=False)
            comment.article = Article.objects.get(id = article_id)
            comment.user = request.user

            comment_id = request.POST.get('parent_id', 0)

            if comment_id != 0:
                parent_comment = get_object_or_404(Comments, id=comment_id)
                comment.parent = parent_comment
            else:
                comment.parent = None
            comment.save()
            messages.success(request, f"Comment added successfully!")
            return redirect(details,article_id)
    return HttpResponse("Something went wrong!")

def load_replies(request, article_id, comment_id):
    if request.method == "GET":
        article = Article.objects.get(id = article_id)
        comment = Comments.objects.get(id=comment_id)
        comments_form = CommentsForm()

        return render(request, "blog/subreplies.html", {"article": article,"replies": comment.children.all(),"comments_form": comments_form})
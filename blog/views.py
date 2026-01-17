from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Post
from django.views.generic import ListView
from django.views import View
from .forms import CommentForm

# Create your views here.


class StartingPageView(ListView):
    template_name = 'blog/index.html'
    model = Post
    ordering = ['-date']
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = super().get_queryset()
        data = queryset[:3]
        return data
    

class PostsView(ListView):
    template_name = 'blog/all-posts.html'
    model = Post
    context_object_name = 'posts'
    ordering = ['-date']
    paginate_by = 10  # Add pagination: 10 posts per page

class PostDetailView(View):

    def is_post_saved(self, request, post_id):
        stored_posts = request.session.get('stored_posts')

        if stored_posts is None:
            is_saved = False
        else:
            is_saved = post_id in stored_posts

        return is_saved
    
    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        return render(request, 'blog/post-detail.html', {
            'post': post,
            'post_tags': post.tags.all(),
            'comment_form': CommentForm(),
            'comments': post.comments.all().order_by('-id'),
            'is_saved': self.is_post_saved(request, post.id)
        })
    
    def post(self, request, slug):
        comment_form = CommentForm(request.POST)
        post = get_object_or_404(Post, slug=slug)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            return HttpResponseRedirect(reverse('post_detail_page', args=[slug]))
        
        return render(request, 'blog/post-detail.html', {
            'post': post,
            'post_tags': post.tags.all(),
            'comment_form': CommentForm(),
            'comments': post.comments.all().order_by('-id'),
            'is_saved': self.is_post_saved(request, post.id)
        })
    
class ReadLaterView(View):
    
    def post(self, request):
        stored_posts = request.session.get('stored_posts')

        if stored_posts is None:
            stored_posts = []

        post_id = int(request.POST['post_id'])

        if post_id not in stored_posts:
            stored_posts.append(post_id)
        else:
            stored_posts.remove(post_id)
            
        request.session['stored_posts'] = stored_posts
        return HttpResponseRedirect('/')
    
    def get(self, request):
        stored_posts = request.session.get('stored_posts')
        context = {}

        if stored_posts is None or len(stored_posts) == 0:
            context['stored_posts'] = []
            context['has_posts'] = False
        else:
            posts = Post.objects.filter(id__in=stored_posts)
            context['posts'] = posts
            context['has_posts'] = True
        
        return render(request, 'blog/stored-posts.html', context)

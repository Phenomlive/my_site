from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Post
from django.views.generic import ListView, DetailView
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

class PostDetailView(View):
    
    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        return render(request, 'blog/post-detail.html', {
            'post': post,
            'post_tags': post.tags.all(),
            'comment_form': CommentForm()
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
            'comment_form': CommentForm()
        })
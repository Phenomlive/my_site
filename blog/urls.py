from django.urls import path

from . import views

urlpatterns = [
    path('', views.StartingPageView.as_view(), name='starting_page'),
    path('posts/', views.PostsView.as_view(), name='posts_page'),
    path('posts/<slug:slug>', views.PostDetailView.as_view(), name='post_detail_page')
]

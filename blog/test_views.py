from django.test import TestCase, Client
from django.urls import reverse
from .models import Post, Author, Comment, Tag
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


def create_test_image():
    """Create a test image file."""
    file = BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'jpeg')
    file.seek(0)
    return SimpleUploadedFile(
        "test_image.jpg",
        file.getvalue(),
        content_type="image/jpeg"
    )


class StartingPageViewTest(TestCase):
    """Tests for the StartingPageView."""
    
    def setUp(self):
        """Create test author and posts."""
        self.client = Client()
        self.author = Author.objects.create(
            first_name='John',
            last_name='Doe',
            email_address='john@example.com'
        )
        # Create 5 posts
        for i in range(5):
            Post.objects.create(
                title=f'Post {i}',
                excerpt=f'Excerpt {i}',
                slug=f'post-{i}',
                content=f'Content for post {i} with minimum length',
                author=self.author,
                image=create_test_image()
            )
    
    def test_starting_page_loads(self):
        """Test that the starting page loads successfully."""
        response = self.client.get(reverse('starting_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/index.html')
    
    def test_starting_page_shows_latest_3_posts(self):
        """Test that starting page shows only the latest 3 posts."""
        response = self.client.get(reverse('starting_page'))
        self.assertEqual(len(response.context['posts']), 3)
    
    def test_starting_page_posts_ordered_by_date(self):
        """Test that posts are ordered by date (newest first)."""
        response = self.client.get(reverse('starting_page'))
        posts = response.context['posts']
        # Posts should be ordered with newest first (descending)
        for i in range(len(posts) - 1):
            self.assertGreaterEqual(posts[i].date, posts[i + 1].date)


class PostsViewTest(TestCase):
    """Tests for the PostsView."""
    
    def setUp(self):
        """Create test author and posts."""
        self.client = Client()
        self.author = Author.objects.create(
            first_name='Jane',
            last_name='Smith',
            email_address='jane@example.com'
        )
        for i in range(3):
            Post.objects.create(
                title=f'Post {i}',
                excerpt=f'Excerpt {i}',
                slug=f'post-{i}',
                content=f'Content ,
                image=create_test_image()for post {i} with minimum length',
                author=self.author
            )
    
    def test_posts_page_loads(self):
        """Test that the all posts page loads successfully."""
        response = self.client.get(reverse('posts_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/all-posts.html')
    
    def test_posts_page_shows_all_posts(self):
        """Test that posts page shows all posts."""
        response = self.client.get(reverse('posts_page'))
        self.assertEqual(len(response.context['posts']), 3)
    
    def test_posts_page_posts_ordered_by_date(self):
        """Test that posts are ordered by date (newest first)."""
        response = self.client.get(reverse('posts_page'))
        posts = response.context['posts']
        for i in range(len(posts) - 1):
            self.assertGreaterEqual(posts[i].date, posts[i + 1].date)


class PostDetailViewTest(TestCase):
    """Tests for the PostDetailView."""
    
    def setUp(self):
        """Create test author and post."""
        self.client = Client()
        self.author = Author.objects.create(
            first_name='John',
            last_name='Doe',
            email_address='john@example.com'
        )
        self.post = Post.objects.create(
            title='Test Post',
            excerpt='Test excerpt',
            slug='test-post',,
            image=create_test_image()
            content='This is test content with minimum length',
            author=self.author
        )
        self.tag = Tag.objects.create(caption='Django')
        self.post.tags.add(self.tag)
    
    def test_post_detail_page_loads(self):
        """Test that the post detail page loads successfully."""
        response = self.client.get(reverse('post_detail_page', args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post-detail.html')
    
    def test_post_detail_page_contains_post(self):
        """Test that the post detail page contains the correct post."""
        response = self.client.get(reverse('post_detail_page', args=[self.post.slug]))
        self.assertEqual(response.context['post'], self.post)
    
    def test_post_detail_page_contains_tags(self):
        """Test that the post detail page contains the post tags."""
        response = self.client.get(reverse('post_detail_page', args=[self.post.slug]))
        self.assertIn(self.tag, response.context['post_tags'])
    
    def test_post_detail_page_contains_comment_form(self):
        """Test that the post detail page contains a comment form."""
        response = self.client.get(reverse('post_detail_page', args=[self.post.slug]))
        self.assertIsNotNone(response.context['comment_form'])
    
    def test_post_detail_page_not_found(self):
        """Test that a 404 is returned for non-existent post."""
        response = self.client.get(reverse('post_detail_page', args=['non-existent']))
        self.assertEqual(response.status_code, 404)
    
    def test_add_comment_to_post(self):
        """Test that a comment can be added to a post."""
        response = self.client.post(
            reverse('post_detail_page', args=[self.post.slug]),
            {
                'user_name': 'Test Commenter',
                'user_mail': 'commenter@example.com',
                'text': 'This is a test comment'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(self.post.comments.count(), 1)
        self.assertEqual(self.post.comments.first().user_name, 'Test Commenter')
    
    def test_is_post_saved_when_not_in_session(self):
        """Test that is_saved is False when post not in session."""
        response = self.client.get(reverse('post_detail_page', args=[self.post.slug]))
        self.assertFalse(response.context['is_saved'])
    
    def test_is_post_saved_when_in_session(self):
        """Test that is_saved is True when post is in session."""
        session = self.client.session
        session['stored_posts'] = [self.post.id]
        session.save()
        
        response = self.client.get(reverse('post_detail_page', args=[self.post.slug]))
        self.assertTrue(response.context['is_saved'])


class ReadLaterViewTest(TestCase):
    """Tests for the ReadLaterView."""
    
    def setUp(self):
        """Create test author and posts."""
        self.client = Client()
        self.author = Author.objects.create(
            first_name='John',
            last_name='Doe',
            email_address='john@example.com'
        )
        self.post1 = Post.objects.create(
            title='Post 1',
            excerpt='Excerpt 1',
            slug='post-1',,
            image=create_test_image()
        )
        self.post2 = Post.objects.create(
            title='Post 2',
            excerpt='Excerpt 2',
            slug='post-2',
            content='Content 2 with minimum length',
            author=self.author,
            image=create_test_image()
            content='Content 2 with minimum length',
            author=self.author
        )
    
    def test_read_later_get_shows_empty_when_no_posts(self):
        """Test that read later page shows empty when no posts saved."""
        response = self.client.get(reverse('read_later_page'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_posts'])
        self.assertEqual(len(response.context['stored_posts']), 0)
    
    def test_read_later_add_post(self):
        """Test that a post can be added to read later."""
        response = self.client.post(
            reverse('read_later_page'),
            {'post_id': self.post1.id}
        )
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertIn(self.post1.id, self.client.session['stored_posts'])
    
    def test_read_later_remove_post(self):
        """Test that a post can be removed from read later."""
        session = self.client.session
        session['stored_posts'] = [self.post1.id]
        session.save()
        
        response = self.client.post(
            reverse('read_later_page'),
            {'post_id': self.post1.id}
        )
        self.assertNotIn(self.post1.id, self.client.session['stored_posts'])
    
    def test_read_later_get_shows_saved_posts(self):
        """Test that read later page shows saved posts."""
        session = self.client.session
        session['stored_posts'] = [self.post1.id, self.post2.id]
        session.save()
        
        response = self.client.get(reverse('read_later_page'))
        self.assertTrue(response.context['has_posts'])
        self.assertEqual(len(response.context['posts']), 2)

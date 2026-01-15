from django.test import TestCase
from .models import Post, Author, Comment
from .forms import CommentForm


class CommentFormTest(TestCase):
    """Tests for the CommentForm."""
    
    def setUp(self):
        """Create test author and post."""
        self.author = Author.objects.create(
            first_name='John',
            last_name='Doe',
            email_address='john@example.com'
        )
        self.post = Post.objects.create(
            title='Test Post',
            excerpt='Test excerpt',
            slug='test-post',
            content='This is test content with minimum length',
            author=self.author
        )
    
    def test_comment_form_valid(self):
        """Test that a valid comment form is accepted."""
        form = CommentForm(data={
            'user_name': 'Test User',
            'user_mail': 'test@example.com',
            'text': 'This is a test comment'
        })
        self.assertTrue(form.is_valid())
    
    def test_comment_form_missing_user_name(self):
        """Test that form is invalid without user name."""
        form = CommentForm(data={
            'user_mail': 'test@example.com',
            'text': 'This is a test comment'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('user_name', form.errors)
    
    def test_comment_form_missing_user_mail(self):
        """Test that form is invalid without user email."""
        form = CommentForm(data={
            'user_name': 'Test User',
            'text': 'This is a test comment'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('user_mail', form.errors)
    
    def test_comment_form_missing_text(self):
        """Test that form is invalid without comment text."""
        form = CommentForm(data={
            'user_name': 'Test User',
            'user_mail': 'test@example.com'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)
    
    def test_comment_form_invalid_email(self):
        """Test that form is invalid with invalid email."""
        form = CommentForm(data={
            'user_name': 'Test User',
            'user_mail': 'invalid-email',
            'text': 'This is a test comment'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('user_mail', form.errors)
    
    def test_comment_form_post_field_excluded(self):
        """Test that the post field is excluded from the form."""
        self.assertNotIn('post', CommentForm().fields)
    
    def test_comment_form_labels(self):
        """Test that form labels are correct."""
        form = CommentForm()
        self.assertEqual(form.fields['user_name'].label, 'Your Name')
        self.assertEqual(form.fields['user_mail'].label, 'Your Email')
        self.assertEqual(form.fields['text'].label, 'Your Comment')
    
    def test_comment_form_save(self):
        """Test that form can save a comment."""
        form = CommentForm(data={
            'user_name': 'Test User',
            'user_mail': 'test@example.com',
            'text': 'This is a test comment'
        })
        self.assertTrue(form.is_valid())
        
        comment = form.save(commit=False)
        comment.post = self.post
        comment.save()
        
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.user_name, 'Test User')
        self.assertEqual(comment.post, self.post)

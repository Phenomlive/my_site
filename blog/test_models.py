from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Post, Author, Comment, Tag


class AuthorModelTest(TestCase):
    """Tests for the Author model."""
    
    def setUp(self):
        """Create a test author."""
        self.author = Author.objects.create(
            first_name='John',
            last_name='Doe',
            email_address='john@example.com'
        )
    
    def test_author_creation(self):
        """Test that an author can be created."""
        self.assertEqual(self.author.first_name, 'John')
        self.assertEqual(self.author.last_name, 'Doe')
        self.assertEqual(self.author.email_address, 'john@example.com')
    
    def test_author_full_name_method(self):
        """Test the full_name method."""
        self.assertEqual(self.author.full_name(), 'John Doe')
    
    def test_author_str_method(self):
        """Test the __str__ method returns full name."""
        self.assertEqual(str(self.author), 'John Doe')


class TagModelTest(TestCase):
    """Tests for the Tag model."""
    
    def setUp(self):
        """Create test tags."""
        self.tag = Tag.objects.create(caption='Django')
    
    def test_tag_creation(self):
        """Test that a tag can be created."""
        self.assertEqual(self.tag.caption, 'Django')
    
    def test_tag_str_method(self):
        """Test the __str__ method returns caption."""
        self.assertEqual(str(self.tag), 'Django')


class PostModelTest(TestCase):
    """Tests for the Post model."""
    
    def setUp(self):
        """Create test author and post."""
        self.author = Author.objects.create(
            first_name='Jane',
            last_name='Smith',
            email_address='jane@example.com'
        )
        self.post = Post.objects.create(
            title='Test Post',
            excerpt='This is a test excerpt',
            slug='test-post',
            content='This is a test content with minimum length',
            author=self.author
        )
    
    def test_post_creation(self):
        """Test that a post can be created."""
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.slug, 'test-post')
        self.assertEqual(self.post.author, self.author)
    
    def test_post_str_method(self):
        """Test the __str__ method returns title."""
        self.assertEqual(str(self.post), 'Test Post')
    
    def test_post_slug_unique(self):
        """Test that post slugs are unique."""
        with self.assertRaises(Exception):
            Post.objects.create(
                title='Another Post',
                excerpt='Another excerpt',
                slug='test-post',
                content='This is another test content',
                author=self.author
            )
    
    def test_post_content_minimum_length_validation(self):
        """Test that content must have minimum length."""
        post = Post(
            title='Short Post',
            excerpt='Short excerpt',
            slug='short-post',
            content='short',
            author=self.author
        )
        with self.assertRaises(ValidationError):
            post.full_clean()
    
    def test_post_tags_relationship(self):
        """Test that tags can be added to posts."""
        tag1 = Tag.objects.create(caption='Django')
        tag2 = Tag.objects.create(caption='Python')
        self.post.tags.add(tag1, tag2)
        
        self.assertEqual(self.post.tags.count(), 2)
        self.assertIn(tag1, self.post.tags.all())
        self.assertIn(tag2, self.post.tags.all())


class CommentModelTest(TestCase):
    """Tests for the Comment model."""
    
    def setUp(self):
        """Create test author, post, and comment."""
        self.author = Author.objects.create(
            first_name='John',
            last_name='Doe',
            email_address='john@example.com'
        )
        self.post = Post.objects.create(
            title='Test Post',
            excerpt='Test excerpt',
            slug='test-post',
            content='This is test content',
            author=self.author
        )
        self.comment = Comment.objects.create(
            user_name='Commenter',
            user_mail='commenter@example.com',
            text='This is a test comment',
            post=self.post
        )
    
    def test_comment_creation(self):
        """Test that a comment can be created."""
        self.assertEqual(self.comment.user_name, 'Commenter')
        self.assertEqual(self.comment.user_mail, 'commenter@example.com')
        self.assertEqual(self.comment.text, 'This is a test comment')
        self.assertEqual(self.comment.post, self.post)
    
    def test_comment_post_relationship(self):
        """Test that comments are related to posts."""
        self.assertEqual(self.post.comments.count(), 1)
        self.assertEqual(self.post.comments.first(), self.comment)
    
    def test_comment_cascade_delete(self):
        """Test that comments are deleted when post is deleted."""
        post_id = self.post.id
        comment_id = self.comment.id
        self.post.delete()
        
        self.assertFalse(Post.objects.filter(id=post_id).exists())
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())

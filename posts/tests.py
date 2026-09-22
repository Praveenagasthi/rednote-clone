from io import BytesIO
from pathlib import Path

from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import (
    Post,
    Like,
    Save,
    Comment,
    Follow,
    Notification,
    Hashtag,
)

User = get_user_model()


class PostAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='postuser',
            email='post@example.com',
            password='StrongPassword@2026'
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='StrongPassword@2026'
        )

        self.client.force_authenticate(
            user=self.user
        )

    def test_create_post(self):
        data = {
            'caption': 'My first test post #test',
            'location': 'India',
        }

        response = self.client.post(
            '/api/posts/',
            data,
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Post.objects.count(),
            1
        )

        post = Post.objects.first()

        self.assertEqual(
            post.author,
            self.user
        )

    def test_create_post_requires_authentication(self):
        self.client.force_authenticate(
            user=None
        )

        data = {
            'caption': 'Unauthorized post'
        }

        response = self.client.post(
            '/api/posts/',
            data,
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_user_can_delete_own_post(self):
        post = Post.objects.create(
            author=self.user,
            caption='Post to delete'
        )

        response = self.client.delete(
            f'/api/posts/{post.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Post.objects.filter(id=post.id).exists()
        )

    def test_user_cannot_delete_other_users_post(self):
        post = Post.objects.create(
            author=self.other_user,
            caption='Other users post'
        )

        response = self.client.delete(
            f'/api/posts/{post.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertTrue(
            Post.objects.filter(id=post.id).exists()
        )

class LikeSaveAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='socialuser',
            email='social@example.com',
            password='StrongPassword@2026'
        )

        self.post = Post.objects.create(
            author=self.user,
            caption='Social action test'
        )

        self.client.force_authenticate(
            user=self.user
        )

    def test_like_post(self):
        response = self.client.post(
            f'/api/posts/{self.post.id}/like/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            response.data['liked']
        )

        self.assertEqual(
            Like.objects.filter(
                user=self.user,
                post=self.post
            ).count(),
            1
        )

    def test_like_toggle_removes_like(self):
        self.client.post(
            f'/api/posts/{self.post.id}/like/'
        )

        response = self.client.post(
            f'/api/posts/{self.post.id}/like/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertFalse(
            response.data['liked']
        )

        self.assertEqual(
            Like.objects.filter(
                user=self.user,
                post=self.post
            ).count(),
            0
        )

    def test_save_post(self):
        response = self.client.post(
            f'/api/posts/{self.post.id}/save/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            response.data['saved']
        )

        self.assertEqual(
            Save.objects.filter(
                user=self.user,
                post=self.post
            ).count(),
            1
        )

    def test_save_toggle_removes_save(self):
        self.client.post(
            f'/api/posts/{self.post.id}/save/'
        )

        response = self.client.post(
            f'/api/posts/{self.post.id}/save/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertFalse(
            response.data['saved']
        )

        self.assertEqual(
            Save.objects.filter(
                user=self.user,
                post=self.post
            ).count(),
            0
        )

class CommentAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='commentuser',
            email='comment@example.com',
            password='StrongPassword@2026'
        )

        self.other_user = User.objects.create_user(
            username='commentother',
            email='commentother@example.com',
            password='StrongPassword@2026'
        )

        self.post = Post.objects.create(
            author=self.user,
            caption='Comment test post'
        )

        self.client.force_authenticate(
            user=self.user
        )

    def test_create_comment(self):
        response = self.client.post(
            f'/api/posts/{self.post.id}/comments/',
            {
                'text': 'This is a test comment.'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['text'],
            'This is a test comment.'
        )

    def test_empty_comment_rejected(self):
        response = self.client.post(
            f'/api/posts/{self.post.id}/comments/',
            {
                'text': '     '
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_user_can_delete_own_comment(self):
        post = Post.objects.create(
            author=self.user,
            caption='Post for comment'
        )

        comment = Comment.objects.create(
            user=self.user,
            post=post,
            text='My comment'
        )

        response = self.client.delete(
            f'/api/posts/comments/{comment.id}/delete/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Comment.objects.filter(id=comment.id).exists()
        )


    def test_user_cannot_delete_other_users_comment(self):
        post = Post.objects.create(
            author=self.user,
            caption='Post for comment'
        )

        comment = Comment.objects.create(
            user=self.other_user,
            post=post,
            text='Other user comment'
        )

        response = self.client.delete(
            f'/api/posts/comments/{comment.id}/delete/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertTrue(
            Comment.objects.filter(id=comment.id).exists()
        )

    def test_comment_nonexistent_post_returns_404(self):
        response = self.client.post(
            '/api/posts/999999/comments/',
            {
                'text': 'Test comment'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

class FollowNotificationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='followuser',
            email='follow@example.com',
            password='StrongPassword@2026'
        )

        self.other_user = User.objects.create_user(
            username='targetuser',
            email='target@example.com',
            password='StrongPassword@2026'
        )

        self.client.force_authenticate(user=self.user)

    def test_user_can_follow_another_user(self):
        response = self.client.post(
            f'/api/auth/users/{self.other_user.id}/follow/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            Follow.objects.filter(
                follower=self.user,
                following=self.other_user
            ).exists()
        )

    def test_follow_toggle_unfollows_user(self):
        Follow.objects.create(
            follower=self.user,
            following=self.other_user
        )

        response = self.client.post(
            f'/api/auth/users/{self.other_user.id}/follow/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertFalse(
            Follow.objects.filter(
                follower=self.user,
                following=self.other_user
            ).exists()
        )

    def test_user_cannot_follow_themselves(self):
        response = self.client.post(
            f'/api/auth/users/{self.user.id}/follow/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertFalse(
            Follow.objects.filter(
                follower=self.user,
                following=self.user
            ).exists()
        )

    def test_follow_creates_notification(self):
        response = self.client.post(
            f'/api/auth/users/{self.other_user.id}/follow/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.other_user,
                sender=self.user,
                notification_type='follow'
            ).exists()
        )

class FeedAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='feeduser',
            email='feed@example.com',
            password='StrongPassword@2026'
        )

        self.followed_user = User.objects.create_user(
            username='followeduser',
            email='followed@example.com',
            password='StrongPassword@2026'
        )

        self.unfollowed_user = User.objects.create_user(
            username='unfolloweduser',
            email='unfollowed@example.com',
            password='StrongPassword@2026'
        )

        self.client.force_authenticate(user=self.user)

    def test_home_feed_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/feed/')

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_home_feed_includes_own_posts(self):
        post = Post.objects.create(
            author=self.user,
            caption='My feed post'
        )

        response = self.client.get('/api/feed/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        post_ids = [
            item['id']
            for item in response.data['results']
        ]

        self.assertIn(post.id, post_ids)

    def test_home_feed_includes_followed_users_posts(self):
        Follow.objects.create(
            follower=self.user,
            following=self.followed_user
        )

        post = Post.objects.create(
            author=self.followed_user,
            caption='Followed user post'
        )

        response = self.client.get('/api/feed/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        post_ids = [
            item['id']
            for item in response.data['results']
        ]

        self.assertIn(post.id, post_ids)

    def test_home_feed_excludes_unfollowed_users_posts(self):
        post = Post.objects.create(
            author=self.unfollowed_user,
            caption='Unfollowed user post'
        )

        response = self.client.get('/api/feed/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        post_ids = [
            item['id']
            for item in response.data['results']
        ]

        self.assertNotIn(post.id, post_ids)

    def test_explore_feed_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/feed/explore/')

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_explore_feed_excludes_own_and_followed_posts(self):
        Follow.objects.create(
            follower=self.user,
            following=self.followed_user
        )

        own_post = Post.objects.create(
            author=self.user,
            caption='My own post'
        )

        followed_post = Post.objects.create(
            author=self.followed_user,
            caption='Followed post'
        )

        explore_post = Post.objects.create(
            author=self.unfollowed_user,
            caption='Explore post'
        )

        response = self.client.get('/api/feed/explore/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        post_ids = [
            item['id']
            for item in response.data['results']
        ]

        self.assertNotIn(own_post.id, post_ids)
        self.assertNotIn(followed_post.id, post_ids)
        self.assertIn(explore_post.id, post_ids)

class HashtagAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='hashtaguser',
            email='hashtag@example.com',
            password='StrongPassword@2026'
        )

        self.other_user = User.objects.create_user(
            username='hashtagother',
            email='otherhashtag@example.com',
            password='StrongPassword@2026'
        )

        self.client.force_authenticate(user=self.user)

    def test_hashtag_posts_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/posts/hashtags/test/')

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_hashtag_returns_matching_posts(self):
        matching_post = Post.objects.create(
            author=self.other_user,
            caption='This is a #Python post'
        )

        hashtag = Hashtag.objects.create(name='python')
        hashtag.posts.add(matching_post)

        response = self.client.get('/api/posts/hashtags/python/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        post_ids = [
            item['id']
            for item in response.data['results']
        ]

        self.assertIn(
            matching_post.id,
            post_ids
        )

    def test_hashtag_does_not_return_unrelated_posts(self):
        matching_post = Post.objects.create(
            author=self.other_user,
            caption='A #Python post'
        )

        unrelated_post = Post.objects.create(
            author=self.other_user,
            caption='A #Django post'
        )

        python_hashtag = Hashtag.objects.create(
            name='python'
        )

        django_hashtag = Hashtag.objects.create(
            name='django'
        )

        python_hashtag.posts.add(matching_post)
        django_hashtag.posts.add(unrelated_post)

        response = self.client.get(
            '/api/posts/hashtags/python/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        post_ids = [
            item['id']
            for item in response.data['results']
        ]

        self.assertIn(
            matching_post.id,
            post_ids
        )

        self.assertNotIn(
            unrelated_post.id,
            post_ids
        )

    def test_hashtag_lookup_is_case_insensitive(self):
        post = Post.objects.create(
            author=self.other_user,
            caption='Testing #Python'
        )

        hashtag = Hashtag.objects.create(
            name='python'
        )

        hashtag.posts.add(post)

        response = self.client.get(
            '/api/posts/hashtags/PYTHON/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        post_ids = [
            item['id']
            for item in response.data['results']
        ]

        self.assertIn(
            post.id,
            post_ids
        )

class PostImageAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='imageuser',
            email='image@example.com',
            password='StrongPassword@2026'
        )

        self.client.force_authenticate(user=self.user)

    def create_test_image(self, name='test.jpg'):
        image = Image.new('RGB', (100, 100), color='red')

        image_file = BytesIO()
        image.save(image_file, format='JPEG')
        image_file.seek(0)

        return SimpleUploadedFile(
            name,
            image_file.read(),
            content_type='image/jpeg'
        )

    def test_post_accepts_image_upload(self):
        image = self.create_test_image()

        response = self.client.post(
            '/api/posts/',
            {
                'caption': 'Post with image',
                'images': image,
            },
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        post = Post.objects.get(
            author=self.user
        )

        self.assertEqual(
            post.images.count(),
            1
        )

    def test_post_accepts_multiple_images(self):
        images = [
            self.create_test_image(f'test{i}.jpg')
            for i in range(3)
        ]

        response = self.client.post(
            '/api/posts/',
            {
                'caption': 'Post with multiple images',
                'images': images,
            },
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        post = Post.objects.get(
            author=self.user
        )

        self.assertEqual(
            post.images.count(),
            3
        )

    def test_post_rejects_more_than_10_images(self):
        images = [
            self.create_test_image(f'test{i}.jpg')
            for i in range(11)
        ]

        response = self.client.post(
            '/api/posts/',
            {
                'caption': 'Too many images',
                'images': images,
            },
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            Post.objects.count(),
            0
        )

    def test_post_rejects_invalid_image(self):
        invalid_image = SimpleUploadedFile(
            'invalid.jpg',
            b'This is not a real image',
            content_type='image/jpeg'
        )

        response = self.client.post(
            '/api/posts/',
            {
                'caption': 'Invalid image',
                'images': invalid_image,
            },
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            Post.objects.count(),
            0
        )

    def test_post_rejects_image_over_10_mb(self):
        # Create a file slightly larger than 10 MB
        oversized_image = SimpleUploadedFile(
            'oversized.jpg',
            b'x' * (10 * 1024 * 1024 + 1),
            content_type='image/jpeg'
        )

        response = self.client.post(
            '/api/posts/',
            {
                'caption': 'Oversized image',
                'images': oversized_image,
            },
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            Post.objects.count(),
            0
        )

    def test_post_image_deleted_when_post_deleted(self):
        image = self.create_test_image()

        response = self.client.post(
            '/api/posts/',
            {
                'caption': 'Image cleanup test',
                'images': image,
            },
            format='multipart'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        post = Post.objects.get(
            author=self.user
        )

        post_image = post.images.first()

        image_path = Path(
            settings.MEDIA_ROOT
        ) / post_image.image.name

        self.assertTrue(
            image_path.exists()
        )

        post.delete()

        self.assertFalse(
            image_path.exists()
        )
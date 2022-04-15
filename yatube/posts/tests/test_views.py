from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestMan')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug_1',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostViewTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug_2',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            group=self.group,
            author=self.user,
            text='Тестовый Текстовый пост ',
        )

    def test_pages_uses_correct_template(self):
        """Проверяем правильные ли html-шаблоны используются."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Главная.Проверяем соответствует ли ожиданиям словарь context."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_title = first_object.group.title
        post_post = first_object.text
        self.assertEqual(post_title, self.group.title)
        self.assertEqual(post_post, self.post.text)

    def test_group_posts_page_show_correct_context(self):
        """Группа.Проверяем соответствует ли ожиданиям словарь context."""
        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_group_description_0 = first_object.group.description
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.group.title)
        self.assertEqual(post_group_description_0, self.group.description)

    def test_profile_page_show_correct_context(self):
        """Профиль.Проверяем соответствует ли ожиданиям словарь context."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'TestMan'})
        )
        first_object = response.context['page_obj'][0]
        profile_title = first_object.group.title
        profile_slug = first_object.group.slug
        profile_text = first_object.text
        self.assertEqual(profile_title, self.group.title)
        self.assertEqual(profile_text, self.post.text)
        self.assertEqual(profile_slug, self.group.slug)

    def test_post_detail_page_show_correct_context(self):
        """Отдельный пост.Проверяем словарь context."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            response.context.get('post').group.title, self.group.title
        )
        self.assertEqual(
            response.context.get('post').group.slug, self.group.slug
        )
        self.assertEqual(response.context.get('post').text, self.post.text)

    def test_create_post_page_show_correct_context(self):
        """Форма создания поста.Проверяем словарь context."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Форма редактирования поста.Проверяем словарь context."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PostPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.numb_obj = settings.OBJ_IN_PAGE
        cls.user = User.objects.create_user(username='TestMan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(16):
            cls.post = Post.objects.create(
                group=cls.group,
                author=cls.user,
                text='Тестовый Текстовый пост ',
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostPaginatorTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.cnt_obj = Post.objects.count()

    def test_first_page_records_index(self):
        """Главная.Проверяем пагинатор на первой странице."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), self.numb_obj)

    def test_second_page_records_index(self):
        """Главная.Проверяем пагинатор на второй странице."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), self.cnt_obj - self.numb_obj
        )

    def test_first_page_records_group_list(self):
        """Группа.Проверяем пагинатор на первой странице группы."""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), self.numb_obj)

    def test_second_page_records_group_list(self):
        """Группа.Проверяем пагинатор на второй странице группы."""
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}) + '?page=2'
        )
        self.assertEqual(len(
            response.context['page_obj']), self.cnt_obj - self.numb_obj
        )

    def test_first_page_records_profile(self):
        """Профиль.Проверяем пагинатор на первой странице."""
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'TestMan'})
        )
        self.assertEqual(len(response.context['page_obj']), self.numb_obj)

    def test_second_page_records_profile(self):
        """Профиль.Проверяем пагинатор на второй странице."""
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': 'TestMan'}) + '?page=2'
        )
        self.assertEqual(len(
            response.context['page_obj']), self.cnt_obj - self.numb_obj
        )

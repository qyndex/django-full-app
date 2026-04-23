"""Factory Boy factories for the blog app."""
import factory
from django.utils.text import slugify

from apps.accounts.tests.factories import UserFactory
from apps.blog.models import Category, Comment, Post, Tag


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    description = factory.Faker("sentence")
    # slug is auto-set by model.save()


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"tag-{n}")
    # slug is auto-set by model.save()


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Sequence(lambda n: f"Post Title {n}")
    author = factory.SubFactory(UserFactory)
    content = factory.Faker("text", max_nb_chars=800)
    excerpt = factory.Faker("sentence")
    status = Post.STATUS_DRAFT
    category = factory.SubFactory(CategoryFactory)


class PublishedPostFactory(PostFactory):
    status = Post.STATUS_PUBLISHED
    published_at = factory.LazyFunction(lambda: __import__("django.utils.timezone", fromlist=["now"]).now())


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    content = factory.Faker("sentence")
    approved = False

"""Factory Boy factories for the accounts app."""
import factory
from django.contrib.auth import get_user_model

from apps.accounts.models import Profile

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class SuperUserFactory(UserFactory):
    is_staff = True
    is_superuser = True


class ProfileFactory(factory.django.DjangoModelFactory):
    """Standalone profile factory — normally the signal handles creation."""

    class Meta:
        model = Profile
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)
    bio = factory.Faker("sentence", nb_words=10)
    website = factory.Faker("url")

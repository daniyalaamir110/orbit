"""Seed a fresh database with a demo account and sample content.

Usage:
    python manage.py seed_demo                 # defaults: 40 users, 5 posts each
    python manage.py seed_demo --users 200 --posts 8
    python manage.py seed_demo --flush         # clear feed data first

Creates a login-ready demo user (demo / SyncoDemo123) plus Faker users with
posts and a few likes. Kept small by default to suit free-tier databases.
"""
import random

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from feed.models import Comment, Like, Post

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with a demo user and sample users/posts."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=40)
        parser.add_argument("--posts", type=int, default=5)
        parser.add_argument("--flush", action="store_true", help="Clear feed data first")

    def handle(self, *args, **opts):
        try:
            from faker import Faker
        except ImportError:
            self.stderr.write("Faker is required (pip install Faker).")
            return

        fake = Faker()
        Faker.seed(7)
        random.seed(7)

        if opts["flush"]:
            Comment.objects.all().delete()
            Like.objects.all().delete()
            Post.objects.all().delete()
            self.stdout.write("Cleared existing feed data.")

        # Demo login account
        demo, created = User.objects.get_or_create(
            username="demo",
            defaults=dict(first_name="Demo", last_name="User", email="demo@orbit.test"),
        )
        if created:
            demo.set_password("SyncoDemo123")
            demo.save()
        self.stdout.write(f"Demo user {'created' if created else 'exists'}: demo / SyncoDemo123")

        pwd = make_password("OrbitPass123")
        used = set(User.objects.values_list("username", flat=True))
        new_users = []
        while len(new_users) < opts["users"]:
            base = fake.user_name()
            uname, n = base, 1
            while uname in used:
                uname = f"{base}{n}"
                n += 1
            used.add(uname)
            new_users.append(
                User(
                    username=uname,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=f"{uname}@orbit.test",
                    password=pwd,
                )
            )
        User.objects.bulk_create(new_users, batch_size=500)
        authors = list(User.objects.filter(username__in=[u.username for u in new_users]))
        authors.append(demo)

        posts = []
        for u in authors:
            for _ in range(opts["posts"]):
                posts.append(Post(author=u, content=fake.sentence(nb_words=random.randint(6, 16))))
        Post.objects.bulk_create(posts, batch_size=1000)

        # A sprinkle of likes
        all_posts = list(Post.objects.all()[:500])
        for _ in range(min(len(all_posts) * 2, 1000)):
            Like.objects.get_or_create(
                post=random.choice(all_posts), user=random.choice(authors)
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded: {User.objects.count()} users, {Post.objects.count()} posts, "
                f"{Like.objects.count()} likes."
            )
        )

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from pages.models import UserProfile

USERNAMES = [
    "CBF114001", "CBF114003", "CBF114004", "CBF114005", "CBF114006",
    "CBF112007", "CBF114008", "CBF114009", "CBF114012", "CBF114013",
    "CBF114015", "CBF114020", "CBF114021", "CBF114024", "CBF114025",
    "CBF114027", "CBF114028", "CBF114029", "CBF114030", "CBF114032",
    "CBF114033", "CBF114035", "CBF114037", "CBF114038", "CBF114039",
    "CBF114041", "CBF114042", "CBF114044", "CBF114045", "CBF114048",
    "CBF114050", "CBF114052", "CBF114055", "CBF114056", "CBF114057",
    "CBF114058", "CBF112059", "CBF114059", "CBF114061",
    "CAA112029",
]

PASSWORD = "20260920"


class Command(BaseCommand):
    help = "Bulk-create student accounts with a shared default password."

    def handle(self, *args, **options):
        created, skipped = 0, 0
        for username in USERNAMES:
            user, was_created = User.objects.get_or_create(username=username)
            if was_created:
                user.set_password(PASSWORD)
                user.save()
                created += 1
            else:
                skipped += 1
            UserProfile.objects.get_or_create(user=user)

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created {created} new user(s), skipped {skipped} existing."
        ))

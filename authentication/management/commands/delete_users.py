from django.core.management.base import BaseCommand
from authentication.models import User

class Command(BaseCommand):
    help = "Deletes Non-Staff Users"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Deleting Non-Staff Users......"))

        users = User.objects.exclude(is_staff = True)
        for user in users:
            user.delete()

        self.stdout.write(self.style.SUCCESS("Non-staff Users deleted Successfully!"))
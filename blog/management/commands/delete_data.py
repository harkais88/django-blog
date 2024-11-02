from django.core.management.base import BaseCommand
from blog.models import Article,ArticleMedia,Tags

class Command(BaseCommand):
    help = "Deletes Data from all Blog models"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Deleting data from models....."))

        self.stdout.write(self.style.SUCCESS("Deleting article media files....."))
        try:
            for articleMedia in ArticleMedia.objects.all():
                articleMedia.delete()
            self.stdout.write(self.style.SUCCESS("All media files deleted"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error Encountered: {e}"))

        self.stdout.write(self.style.SUCCESS("Deleting articles....."))
        try:
            Article.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("All articles deleted"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error Encountered: {e}"))

        self.stdout.write(self.style.SUCCESS("Deleting tags....."))
        try:
            Tags.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("All tags deleted"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error Encountered: {e}"))
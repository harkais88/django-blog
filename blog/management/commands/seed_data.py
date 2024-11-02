from django.core.management.base import BaseCommand, CommandParser
from django.core.management import call_command
from blog.models import Article,ArticleMedia,Tags
from authentication.models import User
from faker import Faker
import random
import requests
from django.core.files.base import ContentFile
from blog.utils import parse_content

class Command(BaseCommand):
    help = "Seeds articles"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--articles", type=int, default=50, help="Number of articles to seed in database")
        parser.add_argument("--number_of_images_in_content", type=int, default=2, 
                            help="Number of images to be included in each content NOTE: Number of paragraphs will be number of images + 1")

    def generate_html(self, number_of_images = 2):
        """ Generates HTML code with image tags"""

        faker = Faker()
        title = faker.sentence(nb_words=6)
        paragraphs = faker.paragraphs(nb=number_of_images+1)
        image_tags = [f'<img src="https://picsum.photos/971/500.jpg?random={random.randint(1,1000)}" alt="Random Image">'
                      for _ in range(number_of_images)]
        sub_content = []
        for index in range(len(image_tags)):
            sub_content.append(f"<p>{paragraphs[index]}</p> {image_tags[index]}")
        sub_content.append(f"<p>{paragraphs[-1]}</p>")

        content = f"""
        <h1>{title}</h1>
        {''.join(sub_content)}
        """

        return content

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Seeding Data....."))

        # Custom Tags
        tags = ['Art', 'Business', 'Children', 'Cooking', 'Culture', 'Design', 'Entertainment', 
                'Environment', 'Fashion', 'Fiction', 'Film', 'Fitness', 'Gadgets', 'Games', 
                'Health', 'History', 'Inspiration', 'Internet', 'Life', 'Marketing', 'News', 
                'Parental', 'Photography', 'Spiritual', 'Sports', 'Technology']
        self.stdout.write(self.style.SUCCESS("Seeding tags....."))
        try:
            for tag in tags:
                Tags.objects.create(name = tag)
            self.stdout.write(self.style.SUCCESS("Tags seeded successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Tags not seeded successfully: Error Occured: {e}"))

        faker = Faker("en_IN")

        self.stdout.write("Checking Users.....")
        if User.objects.exclude(is_staff=True).count() == 0:
            self.stdout.write("No users found, seeding user data")

            number_of_users = 40
            user_input = input("Input the number of users you want to seed (default is 40): ")
            if user_input.isdigit():
                number_of_users = int(user_input)
            else:
                self.stdout.write(self.style.WARNING("Invalid input, proceeding with default value....."))
            call_command("seed_users", users=number_of_users)
        else:
            self.stdout.write(self.style.SUCCESS("Users found"))

        # Generating Articles
        self.stdout.write(self.style.SUCCESS("Seeding Articles....."))
        number_of_articles = options['articles']
        for _ in range(number_of_articles):
            author = User.objects.order_by("?").first()
            title = faker.sentence(nb_words=6)
            content = self.generate_html(number_of_images = options['number_of_images_in_content'])

            # Creating Article Instance
            article = Article.objects.create(
                author = author,
                title = title,
                content = content
            )
            self.stdout.write(self.style.SUCCESS(f"Created article {title} by {author.username}"))

            # Setting tags for Article Instance
            article.tags.set(random.sample(list(Tags.objects.all()), k=random.randint(1,Tags.objects.count())))
            self.stdout.write(
                self.style.SUCCESS(f"Added following tags for article {title} by {author.username}: {", ".join(list(article.tags.values_list("name",flat=True)))}")) 

            # Setting Banner Image for Article Instance
            banner_img_url = f"https://picsum.photos/971/500.jpg?random={random.randint(1,1000)}"
            response = requests.get(banner_img_url)
            if response.status_code == 200:
                filename = f"{article.title}_{article.author}_banner.jpg"
                banner = ContentFile(response.content,filename)
                
                ArticleMedia.objects.create(
                    article = article,
                    image = banner,
                    type = 'BANNER',
                    filename = banner.name,
                    size = banner.size,
                )
                self.stdout.write(self.style.SUCCESS(f"Added banner image for article {title} by {author.username}"))

            # Set up Details Image(s) saving
            self.stdout.write(f"Extracting images from {article.title} content by {article.author.username} and saving to media folder.....")
            content, extracted_image_urls = parse_content(article.content)

            image_url_map = {}
            for index,image_url in enumerate(extracted_image_urls):
                response = requests.get(image_url)
                if response.status_code == 200:
                    filename = f"{article.title}_{article.author}_detail_{index}.png"
                    image_data = ContentFile(response.content,filename)

                    media = ArticleMedia(
                        article = article,
                        image = image_data,
                        type = 'DETAIL',
                        filename = image_data.name,
                        size = image_data.size,
                    )
                    media.save()

                    self.stdout.write(self.style.SUCCESS(f"Successfully extracted image from {article.title} by {article.author.username}"))
                    image_url_map[index] = media.image.url

            for index,url in image_url_map.items():
                content = content.replace(f'src="{index}"', f'src="{url}"')
            
            article.content = content
            article.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully extracted images and altered content for {article.title} by {article.author.username}"))

        self.stdout.write(self.style.SUCCESS("Successfully seeded articles!"))
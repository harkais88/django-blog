from django.core.management.base import BaseCommand, CommandParser
from authentication.models import User
from faker import Faker
from random import choice
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from django.utils import timezone
import requests
from blog.utils import PathAndRename
from django.conf import settings
from pathlib import Path

class Command(BaseCommand):
    help = "Seeds users"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--users', type=int, default=40, help="Number of users to seed in database")

    def generate_about_me(self, username:str):
        """Generates an about me section for a user"""

        faker = Faker("en_IN")
        hobbies = ['learning', 'dancing', 'shopping', 'photography', 'writing', 'exercising', 'woodworking',
                   'painting', 'pottery', 'drawing', 'glassblowing', 'playing', 'playing video games', 'acting',
                   'metalworking', 'knitting', 'roller skating', 'sewing', 'gardening', 'crocheting', 'designing',
                   'web designing', 'cooking', 'coding', 'hiking', 'singing', 'cycling', 'backpacking', 'beekeeping',
                   'playing music', 'brewing', 'writing', 'taking astrophotographs']

        name = username
        hobby = choice(hobbies)
        place = faker.city()
        job = faker.job()
        if ',' in job:
            parts = job.split(", ")
            job = f"{parts[1]} {parts[0]}"

        boilerplates = [
            f"Hello! My name is {name}, and I am a {job}. In my spare time, I enjoy {hobby} and exploring the beautiful sights of {place}. I believe that life is all about experiences, and I’m always on the lookout for new adventures.",
            f"Hey there! I'm {name}, a {job} with a passion for {hobby}. I currently reside in {place}, where I spend my weekends indulging in my interests and meeting new friends. I love sharing my experiences and learning from others.",
            f"Hi! I'm {name}, a proud {job} living in {place}. When I'm not working, you can find me {hobby}. I believe in the importance of balance and love to combine my professional life with my personal passions.",
            f"Greetings! My name is {name}, and I work as a {job}. I have a keen interest in {hobby}, which keeps my creative juices flowing. Residing in {place} allows me to embrace the culture and meet fascinating people.",
            f"Hi everyone! I'm {name}, a {job} who loves {hobby} in my free time. Living in {place} has given me a unique perspective on life, and I enjoy connecting with others who share similar interests."
        ]

        return choice(boilerplates)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Seeding Users"))

        faker = Faker("en_IN")
        path_and_rename = PathAndRename("profile")

        # Getting number of users to be seeded
        number_of_users = options['users']

        # Creating file to record created users
        file = open(f"{Path(settings.BASE_DIR)}/seeded_users.txt","a")
        file.write(f"\n{number_of_users} users created in seeding -- {timezone.now()}")

        self.stdout.write(f"Creating {number_of_users} users......")
        for _ in range(number_of_users):
            while True:
                username = faker.user_name()
                if not User.objects.filter(username = username).exists():
                    break
            while True:
                email = f"{username}-{faker.email()}"
                if not User.objects.filter(email = email).exists():
                    break
            password = faker.password()
            password_hashed = make_password(password)
            gender = choice(['male','female'])
            first_name = faker.first_name_female() if gender == 'female' else faker.first_name_male()
            middle_name = faker.first_name_female() if gender == 'female' else faker.first_name_male()
            last_name = faker.last_name_female() if gender == 'female' else faker.last_name_male()
            about = self.generate_about_me(username)

            user = User.objects.create(
                username = username,
                password = password_hashed,
                first_name = first_name,
                middle_name = middle_name,
                last_name = last_name,
                email = email,
                about = about
            )

            self.stdout.write(self.style.SUCCESS(f"Successfully created user {username}"))
            file.write(f"\n Username: {username}\n Email: {email}\n Password: {password}\n")

            avatar_choices = ['lorelei','adventurer','micah','croodles','notionists']
            avatar_choice = choice(avatar_choices)
            avatar_url = f"https://api.dicebear.com/9.x/{avatar_choice}/jpg?seed={username}"
            response = requests.get(avatar_url)
            if response.status_code == 200:
                profile_picture = ContentFile(response.content, name=f"{username}_profile_pic.png")

                new_filename = path_and_rename(user, f"{username}_profile_pic.png")

                user.profile_picture.save(new_filename, profile_picture)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Successfully added profile picture for user {username}"))
            else:
                self.stdout.write(self.style.ERROR(f"No profile picture added for user {username}"))
        self.stdout.write(self.style.SUCCESS("Users successfully seeded!"))
        file.close()
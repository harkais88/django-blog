import os
from uuid import uuid4
from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

# def get_filename(filename):
#     ext = filename.split(".")[-1]
#     return f"{uuid4()}.{ext}"

# def path_and_rename(path):
#     def wrapper(instance, filename):
#         """ Change the image filename """
#         return os.path.join(path,get_filename(filename))
#     return wrapper

@deconstructible
class PathAndRename(object):
    """Renames the image filename and uploads it to given path"""

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split(".")[-1]
        filename = f"{uuid4()}.{ext}"
        return os.path.join(self.path,filename)

def parse_content(content):
    """Seperates content and images from HTML content"""
    soup = BeautifulSoup(content, 'html.parser')

    # Extracting image sources
    extracted_images_urls = []
    images = soup.find_all('img')

    if images:
        for img in images:
            src = img.get('src')
            if src:
                extracted_images_urls.append(src)

                # Removing src from img
                img['src'] = len(extracted_images_urls) - 1

    content = soup.prettify()

    return content, extracted_images_urls

def validate_image_size(image):
    max_size = 2 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError('Image size is greater than 2MB')
    
def validate_word_count(value):
    word_count = len(value.split())
    if word_count > 250:
        raise ValidationError(f'Word count exceeds the limit of 250 words. Current count: {word_count}')

# def get_absolute_media_url(url):
#     """Cleans the url to get actual media directory path"""
    
#     desired_path = os.path.normpath(url).replace('..' + os.sep, '')
#     return desired_path if desired_path.startswith('/') else "/" + desired_path
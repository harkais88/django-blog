from bs4 import BeautifulSoup
from django import template

register = template.Library()

@register.filter
def add_class_to_images(content, css_class):
    soup = BeautifulSoup(content, 'html.parser')
    for img in soup.find_all('img'):
        img['class'] = img.get('class', []) + [css_class]
    return str(soup)
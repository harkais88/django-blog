from datetime import datetime
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def add_class_to_images(content, css_class):
    soup = BeautifulSoup(content, 'html.parser')
    for img in soup.find_all('img'):
        img['class'] = img.get('class', []) + [css_class]
    return str(soup)

@register.filter
def get_created_at(created_at: datetime):
    rel_diff = relativedelta(timezone.now(), created_at)

    time_str = 'just now'
    if rel_diff.seconds > 0:
        time_str = (f'{rel_diff.seconds} seconds' if rel_diff.seconds > 1 
                    else f'{rel_diff.seconds} second')
    if rel_diff.minutes > 0:
        time_str = (f'{rel_diff.minutes} minutes '+time_str if rel_diff.minutes > 1
                    else f'{rel_diff.minutes} minute')
    if rel_diff.hours > 0:
        time_str = (f'{rel_diff.hours} hours '+time_str if rel_diff.hours > 1
                    else f'{rel_diff.hours} hour')
    if rel_diff.days > 0:
        time_str = (f'{rel_diff.days} days '+time_str if rel_diff.days > 1
                    else f'{rel_diff.days} day')
    if rel_diff.months > 0:
        time_str = (f'{rel_diff.months} months'+time_str if rel_diff.months > 1
                    else f'{rel_diff.months} month')
    if rel_diff.years > 0:
        time_str = (f'{rel_diff.years} years'+time_str if rel_diff.years > 1
                    else f'{rel_diff.years} year')

    return time_str+' ago' if time_str!='just now' else time_str



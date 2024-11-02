from random import randint
from django.core.cache import cache
from django.core.mail import send_mail
from .models import User
from secrets import token_urlsafe
from django.contrib.auth.hashers import make_password
import json
import hashlib
from django.conf import settings
import base64

def send_otp(user: User, timeout = 300):
    """Generate a otp, set it to cache and send it to user email"""

    otp = randint(111111,999999)
    cache.set(key = user.username, value = otp, timeout = timeout)

    send_mail(
        subject=f'{user.username} - OTP Verification',
        message=f'Your otp is {otp}',
        from_email='no-reply@example.com',
        recipient_list=[user.email],
        fail_silently=False 
    )

def get_token():
    """Generate a 32-byte urlsafe token, and return both the token and it's hashed form"""

    token = token_urlsafe(32) # Recommended Bytes to generate good token
    token_hashed = make_password(token)

    return token, token_hashed

def generate_payload_and_signature(token,user,timestamp):
    """Generate an encoded payload and signature for link"""

    payload = {
        'token': token,
        'user_id': user.id,
        'timestamp': timestamp,
    }

    signature = hashlib.sha256(f"{json.dumps(payload)}{settings.SECRET_KEY}".encode()).hexdigest()
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

    return encoded_payload, signature
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from .forms import UserForm
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit
from .models import User, Token
from .utils import send_otp, get_token, generate_payload_and_signature
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
import json
import base64
import hashlib

@ratelimit(key='ip', rate='5/d', method='POST', block=False) 
def register(request):
    context = {
        'form': UserForm(),
    }
    if request.method == 'POST':
        if request.limited:
            context['error'] = 'You have exceeded the number of times you can register, please try again later'
            return render(request,'authentication/register.html',context)

        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
        context['form'] = form    
    return render(request,'authentication/register.html',context)

@ratelimit(key='ip', rate='5/m', method='POST', block=False)
def login(request):
    context = {}
    if request.method == "POST":
        if request.limited:
            context['error'] = 'You have exceeded the number of times you can log in, please try again later'
            return render(request,'authentication/login.html',context)

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request,username = username, password = password)
        if user is not None:
            otp_success = send_otp(request,user)
            if not otp_success:
                return redirect('login')
            return redirect(reverse('otp', kwargs={'username': user.username}))
        context['error'] = 'You have entered the wrong username and/or password'
    return render(request,'authentication/login.html',context)

@ratelimit(key='ip', rate='5/m', method='POST', block=False)
def otp(request,username):
    user = get_object_or_404(User, username = username)
    if user is None:
        return redirect('login')
    
    if 'resend_count' not in request.session:
        request.session['resend_count'] = 0

    context = {'user': user}
    context['resend'] = request.session.pop('resend',None)
    context['error'] = request.session.pop('error',None)
    if request.method == "POST":
        if request.limited:
            context['error'] = "You have exceeded the number of times you can send an otp, please try again later"
            return render(request,'authentication/otp.html',context)

        if 'resend' in request.POST:
            request.session['resend_count'] += 1

            if request.session['resend_count'] >= 5:
                context['error'] = "You have exceeded the number of times you can send an otp, please try again later"
                return render(request,'authentication/otp.html',context)

            send_otp(user)

            request.session['resend'] = 'OTP has been resent successfully!'
            return redirect(reverse('otp', kwargs={'username': user.username}))

        cached_otp = cache.get(user.username)
        if cached_otp is not None:
            otp = request.POST.get('otp')
            if otp is not None and int(otp) == cached_otp:
                auth_login(request, user)
                return redirect('index')
            request.session['error'] = "You have entered the wrong otp, please try again"
            return redirect(reverse('otp', kwargs={'username': user.username}))
        else:
            context['error'] = 'OTP has timed out, try logging in again'
    context['resend_count'] = request.session['resend_count']
    return render(request,'authentication/otp.html',context)

def logout(request):
    auth_logout(request)
    return redirect('login')

@ratelimit(key='ip', rate='3/d', method='POST', block=False)
def password_change_request(request):
    context = {}
    if request.method == 'POST':
        if request.limited:
            context['error'] = 'You have exceeded the number of times you can request for a password change, please try again later'
        else:
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
                if Token.objects.filter(user = user).exists():
                    Token.objects.filter(user = user).delete()

                if user is not None:
                    token, token_hashed = get_token()
                    token_obj = Token.objects.create(
                        user = user,
                        token = token_hashed,
                    )
                    timestamp = token_obj.created_at.timestamp()

                    # Originally was sending token and user id to link, this approach adds a bit more secure
                    payload, signature = generate_payload_and_signature(token, user, timestamp)

                    html_content = render_to_string('authentication/password_email.html',
                                                    context={'host': settings.HOST, 'payload': payload, 'signature': signature})
                    text_content = strip_tags(html_content)

                    email = EmailMultiAlternatives(
                        subject='Blog - Password Reset Request',
                        body=text_content,
                        from_email='no-reply@example.com',
                        to=[user.email]
                    )
                    email.attach_alternative(html_content,'text/html')
                    email.send()
                    
                    context['success'] = "Password Reset Link has been sent to this email"
                else:
                    context['error'] = 'User with this email does not exist'
            except User.DoesNotExist:
                context['error'] = 'User with this email does not exist'
            except ConnectionRefusedError:
                context['error'] = 'Something went wrong, please check your internet connection again, or contact an administrator'

    if request.headers.get('HX-Request'):
        # Build the HTML response directly
        response_html = '<div>'
        if 'success' in context:
            response_html += f'<p class="text-success">{context["success"]}</p>'
            response_html += f'<a href="{reverse("login")}" class="btn btn-custom">Return to Login Page</a>'
        elif 'error' in context:
            response_html += f'<p class="text-danger">{context["error"]}</p><p>Please enter your registered email address to request a password reset.</p>'
        else:
            response_html += '<p>Please enter your registered email address to request a password reset.</p>'
        response_html += '</div>'
        return HttpResponse(response_html)

    return render(request,'authentication/password_change_request.html',context)

# def password_change_verify(request):
#     token = request.GET.get('token')
#     user_id = request.GET.get('user_id')

#     user = User.objects.get(id = user_id)
#     if user is not None:
#         stored_token = Token.objects.get(user = user)    
#         if timezone.now() > stored_token.created_at + timedelta(hours=1):
#             stored_token.delete()
#             return HttpResponse('Token Has expired')
#         if check_password(token,stored_token.token):
#             stored_token.delete()
#             return render(request,'password_change.html', {'user_id': user.id})
#     return HttpResponse("Invalid Token")

def password_change_verify(request):
    data = request.GET.get('data')
    signature = request.GET.get('signature')

    if not data or not signature:
        return HttpResponse('Invalid Link')

    # Extracting payload
    payload = json.loads(base64.urlsafe_b64decode(data).decode())

    # Checking if signature matches 
    expected_signature = hashlib.sha256(f"{json.dumps(payload)}{settings.SECRET_KEY}".encode()).hexdigest()
    if expected_signature != signature:
        return HttpResponse('Invalid Token')

    user_id = payload['user_id']
    try:
        user = User.objects.get(id = user_id)
        stored_token = Token.objects.get(user = user)
        timestamp = payload['timestamp']

        # Checking if token expired
        if stored_token.created_at.timestamp() == timestamp and stored_token.is_expired():
            stored_token.delete()
            return HttpResponse('Token Has expired')
        
        # Checking if token matches with hashed token stored in database
        token = payload['token']
        if check_password(token,stored_token.token):
            stored_token.delete()
            return render(request,'authentication/password_change.html', {'user_id': user.id})

    except User.DoesNotExist:
        return HttpResponse(f'''<p style="color: red;">User does not exist</p>
                            <a href="{settings.HOST}account/login">Go to Login Page</a>''')
    except Token.DoesNotExist:
        return HttpResponse(f'''<p style="color: red">Your request has expired, please try sending another password change request</p>
                            <a href="{settings.HOST}account/login">Go to Login Page</a>''')

def password_change(request):
    context = {}
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = User.objects.get(id = request.POST.get('user_id'))

        if new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            messages.success(request,"Password Changed Successfully! Login Again to Check")
            return redirect('login')    
        context['error'] = 'The password fields do not match'
    return render(request,'authentication/password_change.html',context)

def check_username(request):
    username = request.POST.get('username')

    if User.objects.filter(username = username).exists():
        return HttpResponse("<p class='text-danger'>Username already exists</p>")
    return HttpResponse("<p class='text-success'>Username is available</p>")
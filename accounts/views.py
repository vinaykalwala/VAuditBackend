from email.mime.image import MIMEImage
import random
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth import get_user_model, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from django.core.mail import EmailMultiAlternatives
from email.mime.application import MIMEApplication

# Import from Django REST Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

User = get_user_model()

def generate_otp():
    return str(random.randint(100000, 999999))

from django.core.mail import send_mail
from django.utils.html import format_html
import logging

# Set up logging
logger = logging.getLogger(__name__)
def send_otp_email(email, otp):
    subject = 'Your OTP Code'
    message = f"""
    <html>
    <body>
        <div class="container">
            <div class="header">
                <img src="cid:seo_image" alt="SEO Analysis Image">
            </div>
            <h1>Your OTP Code</h1>
            <p class="otp">{otp}</p>
            <p>This OTP is valid for 5 minutes. If you did not request this OTP, please ignore this email.</p>
            <div class="main-content">
                <img src="cid:logo" alt="Company Logo">
            </div>
            <div class="seo-content">
                <h2>Enhance Your Website with Our SEO Tool</h2>
                <p>Unlock the potential of your website with our cutting-edge SEO tool. Analyze your site's performance, optimize keywords, and monitor your rankings to ensure your website stays ahead of the competition.</p>
            </div>
            <div class="testimonial">
                <h2>What Our Clients Say</h2>
                <p>"Since using this SEO tool, our website traffic has increased by 50% and we have consistently ranked on the first page of search results. Highly recommended!"</p>
                <p>- Jane Doe, Marketing Manager at Example Corp</p>
            </div>
            <div class="cta">
                <h2>Get Started Today!</h2>
                <p>Don't miss out on improving your website's SEO. Start your free trial now and experience the benefits firsthand.</p>
                <a href="https://vindusenvironment.in/signup" style="display:inline-block;padding:10px 20px;background-color:#007bff;color:#ffffff;text-decoration:none;border-radius:5px;">Start Your Free Trial</a>
            </div>
            <div class="footer">
                <p>&copy; 2024 Your Company. All rights reserved.</p>
                <p>Visit our <a href="https://vindusenvironment.in/">website</a> for more information.</p>
            </div>
            <div class="social-media">
                <a href="https://www.facebook.com/yourcompany">
                    <img src="cid:facebook" alt="Facebook" style="width:30px;height:30px;">
                </a>
                <a href="https://www.twitter.com/yourcompany">
                    <img src="cid:twitter" alt="Twitter" style="width:30px;height:30px;">
                </a>
                <a href="https://www.linkedin.com/company/yourcompany">
                    <img src="cid:linkedin" alt="LinkedIn" style="width:30px;height:30px;">
                </a>
                <a href="https://www.instagram.com/yourcompany">
                    <img src="cid:insta" alt="Instagram" style="width:30px;height:30px;">
                </a>
            </div>
        </div>
    </body>
    </html>
    """
    
    from_email = 'no-reply@example.com'
    recipient_list = [email]

    email_message = EmailMultiAlternatives(
        subject,
        '',  # Plain text message is empty
        from_email,
        recipient_list
    )
    email_message.attach_alternative(message, "text/html")

    # Attach images
    try:
        with open('assets/images/seoanalysis.jpg', 'rb') as img:
            seo_image = MIMEImage(img.read())
            seo_image.add_header('Content-ID', '<seo_image>')
            email_message.attach(seo_image)

        with open('assets/images/logo.png', 'rb') as img:
            logo_image = MIMEImage(img.read())
            logo_image.add_header('Content-ID', '<logo>')
            email_message.attach(logo_image)

        with open('assets/images/facebook.png', 'rb') as img:
            facebook_image = MIMEImage(img.read())
            facebook_image.add_header('Content-ID', '<facebook>')
            email_message.attach(facebook_image)

        with open('assets/images/twitter.png', 'rb') as img:
            twitter_image = MIMEImage(img.read())
            twitter_image.add_header('Content-ID', '<twitter>')
            email_message.attach(twitter_image)

        with open('assets/images/linkedin.png', 'rb') as img:
            linkedin_image = MIMEImage(img.read())
            linkedin_image.add_header('Content-ID', '<linkedin>')
            email_message.attach(linkedin_image)

        with open('assets/images/insta.png', 'rb') as img:
            insta_image = MIMEImage(img.read())
            insta_image.add_header('Content-ID', '<insta>')
            email_message.attach(insta_image)

        # Attach PDF
        try:
            with open('assets/files/signup.pdf', 'rb') as pdf_file:
                pdf_attachment = MIMEApplication(pdf_file.read(), _subtype='pdf')
                pdf_attachment.add_header('Content-Disposition', 'attachment', filename='signup.pdf')
                email_message.attach(pdf_attachment)
        except Exception as pdf_error:
            logger.error(f"Error attaching PDF: {pdf_error}")
            raise RuntimeError(f'Failed to attach PDF: {str(pdf_error)}')

        email_message.send()
        logger.info(f'OTP sent successfully to {email}')
        return JsonResponse({'status': 'success', 'otp': otp, 'message': 'OTP sent successfully.'})

    except Exception as e:
        logger.error(f'Failed to send OTP to {email}: {str(e)}')
        raise RuntimeError(f'Failed to send OTP: {str(e)}')
    


@method_decorator(csrf_exempt, name='dispatch')
class SendOTPView(View):
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        otp = generate_otp()

        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required.'}, status=400)

        # Cache the OTP or store in session
        cache.set(f'otp_{email}', otp, timeout=300)  # Expires in 5 minutes

        try:
            # Send OTP to user's email
            send_otp_email(email, otp)
            return JsonResponse({'status': 'success', 'message': 'OTP sent successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Failed to send OTP: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class VerifyOTPView(View):
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        otp = request.POST.get('otp')

        if not email or not otp:
            return JsonResponse({'status': 'error', 'message': 'Email and OTP are required.'}, status=400)

        # Retrieve OTP from cache/session
        cached_otp = cache.get(f'otp_{email}')

        if cached_otp and cached_otp == otp:
            # If OTP matches, remove it from cache
            cache.delete(f'otp_{email}')
            return JsonResponse({'status': 'success', 'message': 'OTP verified successfully.'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid or expired OTP.'}, status=400)

# @method_decorator(csrf_exempt, name='dispatch')
# class SendOTPView(View):
#     def post(self, request, *args, **kwargs):
#         email = request.POST.get('email')
#         otp = generate_otp()

#         if not email:
#             return JsonResponse({'status': 'error', 'message': 'Email is required.'}, status=400)

#         # Cache the OTP or store in session
#         cache.set(f'otp_{email}', otp, timeout=300)  # Expires in 5 minutes

#         try:
#             # Send OTP to user's email
#             send_otp_email(email, otp)
#             # Return the OTP in the response
#             return JsonResponse({'status': 'success', 'message': 'OTP sent successfully.', 'otp': otp}, status=200)
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': f'Failed to send OTP: {str(e)}'}, status=500)


from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            response_data = {
                'token': token.key,
                'username': user.username,
                'is_superuser': user.is_superuser,
                'id': user.id
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class KeywordDataView(APIView):
    def get(self, request, *args, **kwargs):
        # Your logic here
        return Response({'message': 'Keyword data'}, status=status.HTTP_200_OK)


# views.py

from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def verify_otp(request):
    if request.method == 'POST':
        logger.info(f'Request body: {request.body.decode("utf-8")}')
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp = data.get('otp')

            if email and otp:
                # Check if OTP exists and is correct
                stored_otp = cache.get(email)
                if stored_otp and otp == stored_otp:
                    # Invalidate OTP after successful verification
                    cache.delete(email)
                    return JsonResponse({'status': 'success', 'message': 'OTP verified successfully.'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Invalid OTP or email.'}, status=400)
            else:
                return JsonResponse({'status': 'error', 'message': 'Email and OTP are required.'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

def send_otp(email):
    otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
    cache.set(email, otp, timeout=600)  # Store OTP in cache with a timeout (e.g., 10 minutes)
    # Send the OTP to the user via email
    # send_email(email, otp)  # Implement email sending here
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            # Determine the content type and parse data accordingly
            if request.content_type == 'application/x-www-form-urlencoded':
                data = request.POST
            else:
                data = json.loads(request.body)
            
            email = data.get('email')
            password = data.get('password')
            username = data.get('username')
            company_name = data.get('company_name')
            company_size = data.get('company_size')
            seo_proficiency = data.get('seo_proficiency')
            
            # Check if user with the given email already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': 'Email already in use.'}, status=400)
            
            # Create a new user
            user = User(
                email=email,
                username=username,
                company_name=company_name,
                company_size=company_size,
                seo_proficiency=seo_proficiency
            )
            user.set_password(password)  # Hash the password
            user.save()
            
            return JsonResponse({'status': 'success', 'message': 'Signup successful.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

# resetpassword
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

User = get_user_model()

@csrf_exempt
def request_password_reset(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required.'}, status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User with this email does not exist.'}, status=404)
        
        # Generate a token and send email
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        current_site = get_current_site(request)
        subject = 'Password Reset Request'
        message = render_to_string('password_reset_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': uid,
            'token': token,
        })
        
        send_mail(subject, message, 'no-reply@example.com', [email], fail_silently=False)
        
        return JsonResponse({'status': 'success', 'message': 'Password reset email sent.'}, status=200)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

import logging
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger(__name__)

@csrf_exempt
def request_password_reset(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            logger.error('Email not provided')
            return JsonResponse({'status': 'error', 'message': 'Email is required.'}, status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.error(f'User with email {email} does not exist')
            return JsonResponse({'status': 'error', 'message': 'User with this email does not exist.'}, status=404)
        
        otp = user.generate_otp()
        subject = 'Password Reset OTP'
        message = f'Your OTP for password reset is: {otp}'
        try:
            send_mail(subject, message, 'no-reply@example.com', [email], fail_silently=False)
        except Exception as e:
            logger.error(f'Error sending email: {e}')
            return JsonResponse({'status': 'error', 'message': 'Error sending OTP email.'}, status=500)
        
        return JsonResponse({'status': 'success', 'message': 'OTP sent to email.'}, status=200)
    
    logger.error('Invalid request method')
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        logger.debug(f"Received data: {data}")  # Log received data

        email = data.get('email')
        otp = data.get('otp')
        new_password = data.get('new_password')
        
        if not email or not otp or not new_password:
            return JsonResponse({'status': 'error', 'message': 'Email, OTP, and new password are required.'}, status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid email.'}, status=400)
        
        if not user.is_otp_valid(otp):
            return JsonResponse({'status': 'error', 'message': 'Invalid or expired OTP.'}, status=400)
        
        user.set_password(new_password)
        user.save()
        
        return JsonResponse({'status': 'success', 'message': 'Password reset successfully.'}, status=200)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

# payment process
import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from .models import Payment

logger = logging.getLogger(__name__)
@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        try:
            logger.info("Received POST request for processing payment.")

            # Authenticate user via token
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                logger.error("Authorization token is missing.")
                return JsonResponse({'error': 'Authorization token is missing.'}, status=401)

            token = auth_header.split(" ")[1]  # Extract token from the Authorization header
            try:
                token_obj = Token.objects.get(key=token)  # Fetch the token object
                user = token_obj.user  # Get the authenticated User instance
                logger.info(f"User authenticated: {user.id}")
            except Token.DoesNotExist:
                logger.error("Invalid or expired token.")
                return JsonResponse({'error': 'Invalid or expired token.'}, status=401)

            # Parse the JSON request body
            try:
                data = json.loads(request.body)
                logger.info(f"Received payment data: {data}")
            except json.JSONDecodeError:
                logger.error("Invalid JSON data.")
                return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

            # Extract and validate required fields
            plan = data.get('plan')
            price = data.get('price')
            payment_id = data.get('paymentId')

            if not plan or price is None or not payment_id:
                logger.error("Plan, price, or payment ID is missing.")
                return JsonResponse({'error': 'Plan, price, and payment ID are required.'}, status=400)

            try:
                price = float(price)
                if price < 0:
                    raise ValueError("Price must be a positive number.")
            except ValueError as ve:
                logger.error(f"Invalid price: {ve}")
                return JsonResponse({'error': f'Invalid price: {ve}'}, status=400)

            # Save payment details
            payment = Payment.objects.create(
                user=user,          # ForeignKey relationship with the User instance
                user_id=user.id,    # Explicitly storing the user ID
                plan=plan,
                price=price,
                payment_id=payment_id
            )

            logger.info(f"Payment details saved: {payment.id}")

            return JsonResponse(
                {
                    'message': 'Payment details saved successfully!',
                    'payment': {
                        'user_id': payment.user_id,   # Return the stored user ID
                        'plan': payment.plan,
                        'price': payment.price,
                        'payment_id': payment.payment_id,
                        'created_at': payment.created_at,
                    },
                },
                status=200
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method. Only POST is allowed.'}, status=405)

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required(login_url='/login/')
def check_user_subscription(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    user = request.user
    has_subscription = Payment.objects.filter(user=user, plan__isnull=False).exclude(plan="").exists()
    return JsonResponse({'has_subscription': has_subscription})

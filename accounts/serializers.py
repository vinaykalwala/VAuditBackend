from rest_framework import serializers
from .models import User
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(write_only=True, required=False)
    otp_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'username', 'first_name', 'last_name', 'company_name', 'company_size', 'seo_proficiency', 'otp', 'otp_verified']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        otp = validated_data.pop('otp', None)
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        if otp:
            if user.otp == otp and user.otp_expires_at > timezone.now():
                user.otp_verified = True
                user.save()
            else:
                raise serializers.ValidationError("Invalid or expired OTP")
        return user

from rest_framework import serializers
from .models import Payment
from .models import User  # Import User model

class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Serialize only the user ID

    class Meta:
        model = Payment
        fields = ['user', 'plan', 'price', 'payment_id', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)



from copy import deepcopy
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers
import re

from .constants import NAME_REGEX, EMAIL_REGEX
from .models import Profile


User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    # These fields are not present in the User model
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    date_of_birth = serializers.DateField(write_only=True)
    photo = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name',
            'username', 'email',
            'password1', 'password2',
            'date_of_birth', 'photo',
        )

    def validate_first_name(self, first_name):
        """Validates the first name field against a regex pattern."""
        cleaned_first_name = first_name.strip()
        if not re.fullmatch(NAME_REGEX, cleaned_first_name):
            raise serializers.ValidationError(
                f"Invalid first name: '{first_name}' - must have only 10 regular/accented letters."
            )
        return cleaned_first_name
        
    def validate_last_name(self, last_name):
        """Validates the last name field against a regex pattern."""
        cleaned_last_name = last_name.strip()
        if not re.fullmatch(NAME_REGEX, cleaned_last_name):
            raise serializers.ValidationError(
                f"Invalid last name: '{last_name}' - must have only 10 regular/accented letters."
            )
        return cleaned_last_name

    def validate_username(self, username: str = ""):
        """Checks if username already exists in the database."""
        cleaned_username: str = username.strip()

        if User.objects.filter(username=cleaned_username).exists():
            raise serializers.ValidationError(
                f"Username '{username}' already exists."
            )
        return cleaned_username

    def validate_email(self, email):
        """Validates the email field against a regex pattern."""
        cleaned_email = email.strip()
        if not re.fullmatch(EMAIL_REGEX, cleaned_email):
            raise serializers.ValidationError(
                f"Invalid email: '{email}'"
                " - username must have only letters/numbers/'.'/'-'/'_'/'%'/'+'"
                ", followed by '@'"
                ", followed by domain name that must have only letters/numbers/'.'/'-'"
                ", followed by '.'"
                ", followed by TLD name that must have min. 2 letters."
            )
        
        if User.objects.filter(email=cleaned_email).exists():
                raise serializers.ValidationError(
                    f"Email '{email}' already exists."
                )
        
        return cleaned_email
    
    def validate_password1(self, password1):
        """Validates password against a list of criteria."""
        checks = {
            "Length must be between 8 and 16 characters.":
                8 <= len(password1) <= 16,
            "Must contain at least one uppercase letter.":
                any(c.isupper() for c in password1),
            "Must contain at least one lowercase letter.":
                any(c.islower() for c in password1),
            "Must contain at least one number.":
                any(c.isdigit() for c in password1),
            "Must contain at least one special character.":
                bool(re.search(
                    r"[!@#\$%\^&\*\(\)_\+\-=\[\]\{\};':\"\\\|,.<>\/?]",
                    password1
                ))
        }
    
        errors = "\n".join(msg for msg, passed in checks.items() if not passed)
    
        if errors:
            raise serializers.ValidationError(errors)
        
        return password1

    def validate_date_of_birth(self, dob):
        """Validates DOB against today, future, and an age range of 18-120."""
        today = date.today()
        age: int = relativedelta(today, dob).years
        if dob > today:
            raise serializers.ValidationError(
                f"Invalid date of birth: '{dob}' - DOB in the future."
            )
        elif age < 18:
            raise serializers.ValidationError(
                f"Not an adult: '{dob}' - must be at least 18 years old."
            )
        elif age > 120:
            raise serializers.ValidationError(
                f"Unrealistically old: '{dob}' - must be at most 120 years old."
            )
        else:
            return dob

    def validate_photo(self, photo):
        """Validates photo size and type."""

        if not photo:
            return photo
        
        max_size = 5 * 1024 * 1024
        if photo.size > max_size:
            raise serializers.ValidationError(
                'Profile picture cannot exceed 5 MB.'
            )

        allowed_types = (
            'image/jpeg', 'image/png', 'image/webp',
        )
        if photo.content_type not in allowed_types:
            raise serializers.ValidationError(
                'Only JPEG, PNG and WebP images are allowed.'
            )

        return photo

    def validate(self, attrs):
        """Validates password and username/email uniqueness."""
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError(
                'Passwords do not match.'
            )

        if attrs['password1'] == attrs['username']:
            raise serializers.ValidationError(
                'Password cannot be the same as username.'
            )

        if attrs['username'] == attrs['email']:
            raise serializers.ValidationError(
                'Username and email cannot be the same.'
            )
        
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Creates user and profile."""
        date_of_birth = validated_data.pop('date_of_birth')
        photo = validated_data.pop('photo', None)
        password = validated_data.pop('password1')
        validated_data.pop('password2')

        user = User.objects.create_user(
            **validated_data, password=password
        )

        Profile.objects.create(
            user=user,
            date_of_birth=date_of_birth,
            photo=photo,
        )

        return user


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        source='user.first_name', required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        source='user.last_name', required=False, allow_blank=True
    )
    username = serializers.CharField(
        source='user.username', required=False, allow_blank=True
    )
    email = serializers.EmailField(
        source='user.email', required=False, allow_blank=True
    )
    class Meta:
        model = Profile
        fields = (
            'first_name', 'last_name',
            'username', 'email',
            'date_of_birth', 'photo'
        )

    def validate_first_name(self, first_name):
        """Validates the first name field against a regex pattern."""
        cleaned_first_name = first_name.strip()
        if not re.fullmatch(NAME_REGEX, cleaned_first_name):
            raise serializers.ValidationError(
                f"Invalid first name: '{first_name}' - must have only 10 regular/accented letters."
            )
        return cleaned_first_name
        
    def validate_last_name(self, last_name):
        """Validates the last name field against a regex pattern."""
        cleaned_last_name = last_name.strip()
        if not re.fullmatch(NAME_REGEX, cleaned_last_name):
            raise serializers.ValidationError(
                f"Invalid last name: '{last_name}' - must have only 10 regular/accented letters."
            )
        return cleaned_last_name

    def validate_username(self, username: str = ""):
        """
        Checks if username already exists in the database, excluding the current user.
        """
        cleaned_username: str = username.strip()

        qs = Profile.objects.select_related('user').filter(user__username=cleaned_username)

        if self.instance:
            qs = qs.exclude(user=self.instance.user)

        if qs.exists():
            raise serializers.ValidationError(
                f"Username '{username}' already exists."
            )
        return cleaned_username

    def validate_email(self, email):
        """Validates the email field against a regex pattern."""
        cleaned_email = email.strip()
        if not re.fullmatch(EMAIL_REGEX, cleaned_email):
            raise serializers.ValidationError(
                f"Invalid email: '{email}'"
                " - username must have only letters/numbers/'.'/'-'/'_'/'%'/'+'"
                ", followed by '@'"
                ", followed by domain name that must have only letters/numbers/'.'/'-'"
                ", followed by '.'"
                ", followed by TLD name that must have min. 2 letters."
            )
        return cleaned_email

    def validate_date_of_birth(self, dob):
        """Validates DOB against today, future, and an age range of 18-120."""
        today = date.today()
        age: int = relativedelta(today, dob).years
        if dob > today:
            raise serializers.ValidationError(
                f"Invalid date of birth: '{dob}' - DOB in the future."
            )
        elif age < 18:
            raise serializers.ValidationError(
                f"Not an adult: '{dob}' - must be at least 18 years old."
            )
        elif age > 120:
            raise serializers.ValidationError(
                f"Unrealistically old: '{dob}' - must be at most 120 years old."
            )
        else:
            return dob

    def validate_photo(self, photo):
        """Validates photo size and type."""

        if not photo:
            return photo
        
        max_size = 5 * 1024 * 1024
        if photo.size > max_size:
            raise serializers.ValidationError(
                'Profile picture cannot exceed 5 MB.'
            )

        allowed_types = (
            'image/jpeg', 'image/png', 'image/webp',
        )
        if photo.content_type not in allowed_types:
            raise serializers.ValidationError(
                'Only JPEG, PNG and WebP images are allowed.'
            )

        return photo

    def validate(self, attrs):
        """
        Validates all the fields and runs model validation
        without mutating the existing instances.
        """
        # Extract the nested dictionary DRF created
        user_data = attrs.get('user', {})
        
        # For PATCH requests, fields might be missing. Fall back to existing instance.
        current_username = user_data.get(
            'username', self.instance.user.username if self.instance else None
        )
        current_email = user_data.get(
            'email', self.instance.user.email if self.instance else None
        )

        if current_username and current_email and current_username == current_email:
            raise serializers.ValidationError(
                'Username and email cannot be the same.'
            )
        
        user_copy = deepcopy(self.instance.user)
        profile_copy = deepcopy(self.instance)

        try:
            # Apply the nested 'user' data to the User model copy
            if 'user' in attrs:
                for field, value in attrs['user'].items():
                    setattr(user_copy, field, value)
            
            # Apply everything else to the Profile model copy
            for field, value in attrs.items():
                if field != 'user':
                    setattr(profile_copy, field, value)

            user_copy.full_clean()
            profile_copy.full_clean()

        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        """Updates the profile and related user instance."""
        
        # Pop the nested user dictionary entirely out of validated_data
        user_data = validated_data.pop('user', {})
        
        # Update the User model
        for field, value in user_data.items():
            setattr(instance.user, field, value)
            
        # Update the Profile model with whatever is left in validated_data
        for field, value in validated_data.items():
            setattr(instance, field, value)
            
        instance.user.save()
        instance.save()

        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        write_only=True,
        style={'input_type': 'text'},
        required=True
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        required=True
    )

    def validate_username(self, username):
        """Checks if the entered username is empty."""
        cleaned_username = username.strip()
        if not cleaned_username:
            raise serializers.ValidationError(
                'Username cannot be empty.'
            )
        return cleaned_username

    def validate(self, attrs):
        request = self.context.get('request')

        user = authenticate(
            request=request,
            username=attrs['username'],
            password=attrs['password']
        )
        # This returns a valid user but
        # doesn't set the user in the
        # request, that's the job of
        # Django's login() method

        # I need to manually set the user
        # in the request using the tokens
        # so that the templates can work

        # The best way might be to use a
        # custom middleware as it intercepts
        # every request/response.

        if not user:
            raise serializers.ValidationError(
                'Invalid username or password.'
        )

        attrs['user'] = user
        return attrs
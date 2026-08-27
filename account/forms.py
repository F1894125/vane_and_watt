from datetime import date
from dateutil.relativedelta import relativedelta
import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .constants import NAME_REGEX, EMAIL_REGEX
from .models import Profile


User = get_user_model()


class RegistrationForm(UserCreationForm):
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={'type': 'date'}
        )
    )
    photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name',
            'username', 'email',
            'password1', 'password2',
            'date_of_birth', 'photo',
        )

    def clean_first_name(self, first_name):
        """Validates the first name field against a regex pattern."""
        cleaned_first_name = first_name.strip()
        if not re.fullmatch(NAME_REGEX, cleaned_first_name):
            raise ValidationError(
                f"Invalid first name: '{first_name}' - must have only 10 regular/accented letters."
            )
        return cleaned_first_name
        
    def clean_last_name(self, last_name):
        """Validates the last name field against a regex pattern."""
        cleaned_last_name = last_name.strip()
        if not re.fullmatch(NAME_REGEX, cleaned_last_name):
            raise ValidationError(
                f"Invalid last name: '{last_name}' - must have only 10 regular/accented letters."
            )
        return cleaned_last_name

    def clean_username(self, username: str = ""):
        """Checks if username already exists in the database."""
        cleaned_username: str = username.strip()

        qs = Profile.objects.select_related('user').filter(user__username=cleaned_username)

        if qs.exists():
            raise ValidationError(
                f"Username '{username}' already exists."
            )
        return cleaned_username

    def clean_email(self, email):
        """Validates the email field against a regex pattern."""
        cleaned_email = email.strip()
        if not re.fullmatch(EMAIL_REGEX, cleaned_email):
            raise ValidationError(
                f"Invalid email: '{email}'"
                " - username must have only letters/numbers/'.'/'-'/'_'/'%'/'+'"
                ", followed by '@'"
                ", followed by domain name that must have only letters/numbers/'.'/'-'"
                ", followed by '.'"
                ", followed by TLD name that must have min. 2 letters."
            )
        return cleaned_email
    
    def clean_password1(self, password1):
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
            raise ValidationError(errors)
        
        return password1

    def clean_date_of_birth(self, dob):
        """Validates DOB against today, future, and an age range of 18-120."""
        today = date.today()
        age: int = relativedelta(today, dob).years
        if dob > today:
            raise ValidationError(
                f"Invalid date of birth: '{dob}' - DOB in the future."
            )
        elif age < 18:
            raise ValidationError(
                f"Not an adult: '{dob}' - must be at least 18 years old."
            )
        elif age > 120:
            raise ValidationError(
                f"Unrealistically old: '{dob}' - must be at most 120 years old."
            )
        else:
            return dob

    def clean_photo(self, photo):
        """Validates photo size and type."""

        if not photo:
            return photo
        
        max_size = 5 * 1024 * 1024
        if photo.size > max_size:
            raise ValidationError(
                'Profile picture cannot exceed 5 MB.'
            )

        allowed_types = (
            'image/jpeg', 'image/png', 'image/webp',
        )
        if photo.content_type not in allowed_types:
            raise ValidationError(
                'Only JPEG, PNG and WebP images are allowed.'
            )

        return photo

    def clean(self):
        """Validates password and username/email uniqueness."""
        cleaned_data = super().clean()
        if cleaned_data['password1'] != cleaned_data['password2']:
            raise ValidationError(
                'Passwords do not match.'
            )

        if cleaned_data['password1'] == cleaned_data['username']:
            raise ValidationError(
                'Password cannot be the same as username.'
            )

        if cleaned_data['username'] == cleaned_data['email']:
            raise ValidationError(
                'Username and email cannot be the same.'
            )
        
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        ),
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        ),
        required=True
    )

    def clean_username(self, username):
        """Checks if the entered username is empty."""
        cleaned_username = username.strip()
        if not cleaned_username:
            raise ValidationError(
                'Username cannot be empty.'
            )
        return cleaned_username


class ProfileEditForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    photo = forms.ImageField(required=False)
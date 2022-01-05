from django_registration.forms import RegistrationForm
from users.models import CustomUser

# https://django-registration.readthedocs.io/en/3.2/custom-user.html
class CustomUserForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = CustomUser

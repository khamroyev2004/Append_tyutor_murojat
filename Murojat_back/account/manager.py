from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):

    def create_user(self, hemis, password=None, **extra_fields):
        if not hemis:
            raise ValueError('Users must have an email address')

        user = self.model(hemis=hemis, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, hemis, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(hemis, password, **extra_fields)

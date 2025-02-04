from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    user_type = models.CharField(
        max_length=20,
        choices=[('ADMIN', 'Admin'), ('LAWYER', 'Lawyer'),
                 ('JUDGE', 'Judge'), ('CITIZEN', 'Citizen')],
        default='ADMIN'
    )
    full_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    # contact_type = models.CharField(max_length=10)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    groups = models.ManyToManyField(
        Group, related_name='custom_user_set', blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission, related_name='custom_user_permissions_set', blank=True
    )

    def __str__(self):
        return self.username

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_superuser = models.BooleanField(default=True)

    def __str__(self):
        return f"Admin - {self.user.username}"

class Lawyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50, unique=True)
    law_firm = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=15, blank=True, null=True)
    branch_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Lawyer - {self.user.username}"

class Judge(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    court = models.CharField(max_length=100)
    cases_assigned = models.IntegerField(default=0)

    def __str__(self):
        return f"Judge - {self.user.username}"

class Citizen(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    national_id_type = models.CharField(max_length=20)
    national_id = models.CharField(max_length=20, unique=True)
    cases_filed = models.IntegerField(default=0)

    def __str__(self):
        return f"Citizen - {self.user.username}"
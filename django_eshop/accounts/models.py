from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MyAccountManager(BaseUserManager):                                                                                #creation, deletion, retrieval of users
    def create_user(self,first_name,last_name,username,email,password=None):                                            #custom model for creating a user, will supplement
        if not email:                                                                                                   #the django's default user model
            raise ValueError('Email address is a mandatory field')

        if not username:
            raise ValueError ('Username is a mandatory field')

        user= self.model(
            email = self.normalize_email(email),                                                                        #Uppercase will get converted to lowercase
            username = username,
            first_name = first_name,
            last_name = last_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):                                       # fields required for creating the superuser
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )

        user.is_admin= True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):                                                                                        #governs users behavior
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(max_length=150, unique=True)
    phone_number = models.CharField(max_length=100)

                                                                                                                        #mandatory fields for custom user model
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin =models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'                                                                                            #logging in with email                                                                                #logging in with email address
    REQUIRED_FIELDS = ['username','first_name','last_name']

    objects = MyAccountManager()

    class Meta:
        verbose_name = 'account'
        verbose_name_plural = 'accounts'

    def full_name(self):
        return f'{self.first_name}{self.last_name}'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin                                                                                            #if an admin, then  has all the privileges

    def has_module_perms(self, add_label):
        return True

class UserProfile(models.Model):
    #FK
    user= models.OneToOneField(Account,on_delete=models.CASCADE)                                                        #only one profile associated with one account
    address_1=models.CharField(blank=True,max_length=300)
    address_2=models.CharField(blank=True,max_length=300)
    profile_picture=models.ImageField(blank=True,upload_to='userprofile')
    city=models.CharField(blank=True,max_length=150)
    state=models.CharField(blank=True,max_length=150)
    country=models.CharField(blank=True,max_length=150)

    def __str__(self):
        return self.user.first_name

    def full_address(self):
        return f'{self.address_1} {self.address_2}'

class EmailNewsLetter(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email



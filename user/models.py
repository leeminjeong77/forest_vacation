from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, student_num, password=None, **extra_fields):
        if not student_num:
            raise ValueError("학번은 필수 입력 항목입니다.")
        user= self.model(student_num=student_num, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, student_num, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        
        return self.create_user(student_num, password, **extra_fields)


class User(AbstractBaseUser):
    student_num = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    point = models.IntegerField(default=0)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    nickname = models.CharField(max_length=30, blank=True, null=True)

   
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "student_num"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.student_num

    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin
    
    class Meta:
        db_table = 'user'
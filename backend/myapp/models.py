from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Make sure we're using the right JSONField import based on Django version
try:
    # For Django 3.1+
    from django.db.models import JSONField
except ImportError:
    # For Django 3.0 and below with postgres
    from django.contrib.postgres.fields import JSONField

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    )
    
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Make sure the JSONField is correctly initialized
    coursesWithGrades = JSONField(default=list, blank=True, null=True)
    
    # Add the university foreign key field
    university = models.ForeignKey(
        'University',  # This references the University model
        on_delete=models.SET_NULL,  # When a university is deleted, set the field to NULL
        null=True,  # Allow the field to be NULL (not all users need a university)
        blank=True,  # Allow the field to be blank in forms
        related_name='users',  # Allows University.users.all() to get all users from a university
        verbose_name='University'
    )
    
    # Override the related_name for groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='myapp_user_set',
        related_query_name='myapp_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='myapp_user_set',
        related_query_name='myapp_user'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"
    
class University(models.Model):
    name = models.CharField(max_length=200, verbose_name="University Name")
    location = models.CharField(max_length=200, verbose_name="Location")
    foundation_year = models.IntegerField(verbose_name="Year of Foundation")
    students = models.IntegerField(verbose_name="Number of Students", default=0)
    website = models.URLField(max_length=200, verbose_name="Website", blank=True, null=True)
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.location})"
    
    class Meta:
        verbose_name = "University"
        verbose_name_plural = "Universities"
        ordering = ['name']

class Course(models.Model):
    COURSE_TYPES = (
        ('mandatory', 'Mandatory'),
        ('optional', 'Optional'),
    )
    
    name = models.CharField(max_length=200, verbose_name="Course Name")
    credits = models.IntegerField(verbose_name="Credits")
    professor = models.CharField(max_length=200, verbose_name="Professor", blank=True, null=True)
    type = models.CharField(max_length=20, choices=COURSE_TYPES, default='mandatory')
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name="University"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.university.name})"
    
    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ['name']

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, University

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'status', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('role', 'status', 'is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'name', 'password1', 'password2', 'role', 'status'),
        }),
    )
    search_fields = ('email', 'name', 'username')
    ordering = ('email',)

class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'foundation_year', 'students', 'created_at')
    list_filter = ('location',)
    search_fields = ('name', 'location')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(User, CustomUserAdmin)
admin.site.register(University, UniversityAdmin)

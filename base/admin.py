from django.contrib import admin
from base.models import User
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea, CharField
from django import forms
from django.db import models


class UserAdminConfig(UserAdmin):
    model = User
    search_fields = ('email', 'first_name', 'phone_number')
    list_filter = ('is_active', 'is_staff')
    ordering = ('-created_at',)
    list_display = ('email', 'first_name', 'phone_number',
                    'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'first_name',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Personal', {'fields': ('about','phone_number')}),
    )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 60})},
    }
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'password1', 'password2', 'is_active', 'is_staff')}
         ),
    )


admin.site.register(User, UserAdminConfig)
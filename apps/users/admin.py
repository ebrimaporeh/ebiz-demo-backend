from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display   = ('email', 'name', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter    = ('role', 'is_active', 'is_staff')
    search_fields  = ('email', 'name')
    ordering       = ('-date_joined',)
    fieldsets = (
        (None,           {'fields': ('email', 'password')}),
        ('Personal',     {'fields': ('name',)}),
        ('Platform role',{'fields': ('role',)}),
        ('Permissions',  {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates',        {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'name', 'role', 'password1', 'password2')}),
    )
    readonly_fields = ('date_joined', 'last_login')

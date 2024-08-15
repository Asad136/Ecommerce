from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.core.mail import send_mail


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'is_verified')}),
    )
    list_display = ('username', 'email', 'role', 'is_verified')

    def save_model(self, request, obj, form, change):
        if 'is_verified' in form.changed_data:
            if obj.is_verified:
                subject = 'Congratulations! Your account is verified.'
                message = 'You can now make your account and start selling.'
                from_email = 'eccomerces@example.com'
                recipient_list = [obj.email]
                send_mail(subject, message, from_email, recipient_list)
        super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)
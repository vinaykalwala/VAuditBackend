# admin.py
from django.contrib import admin
from .models import User
from .models import Payment

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Payment)




# Optionally, customize LogEntry if needed
# class LogEntryAdmin(admin.ModelAdmin):
#     list_display = ['user', 'action_time', 'content_type', 'object_id', 'object_repr', 'action_flag']
# admin.site.register(LogEntry, LogEntryAdmin)

from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'age', 'risk_score', 'blood_glucose']
    list_filter = ['gender', 'takes_medication']
    search_fields = ['full_name', 'user__username']

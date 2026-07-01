from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class DailyCheckIn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkins')
    date = models.DateField(default=timezone.localdate)

    # Section 1 — Medical indicators
    glucose_fasting   = models.FloatField(null=True, blank=True)
    glucose_postmeal  = models.FloatField(null=True, blank=True)
    bp_systolic       = models.PositiveSmallIntegerField(null=True, blank=True)
    bp_diastolic      = models.PositiveSmallIntegerField(null=True, blank=True)
    pulse             = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg         = models.FloatField(null=True, blank=True)

    # Section 2 — Medicine intake
    medicine_name  = models.CharField(max_length=150, blank=True)
    medicine_taken = models.BooleanField(null=True)
    medicine_time  = models.TimeField(null=True, blank=True)
    skip_reason    = models.TextField(blank=True)

    # Section 3 — Lifestyle
    breakfast          = models.CharField(max_length=255, blank=True)
    lunch              = models.CharField(max_length=255, blank=True)
    dinner             = models.CharField(max_length=255, blank=True)
    physical_activity  = models.CharField(max_length=255, blank=True)
    activity_duration  = models.PositiveSmallIntegerField(null=True, blank=True)
    sleep_hours        = models.FloatField(null=True, blank=True)
    stress_level       = models.PositiveSmallIntegerField(null=True, blank=True)

    # Section 4 — Symptoms (comma-separated)
    symptoms = models.TextField(blank=True)

    # Section 5 — Wellbeing
    wellbeing_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} — {self.date}"


class Alert(models.Model):
    ALERT_TYPES = [
        ('high_glucose',    'Yuqori qand'),
        ('low_glucose',     'Past qand'),
        ('missed_medicine', 'Dori o\'tkazib yuborildi'),
        ('high_bp',         'Yuqori qon bosimi'),
        ('side_effects',    'Nojo\'ya ta\'sirlar'),
        ('no_data',         'Ma\'lumot yo\'q'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.alert_type}"

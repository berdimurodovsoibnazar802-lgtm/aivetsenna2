from django.db import models
from django.conf import settings


class Profile(models.Model):
    GENDER_CHOICES = [('male', 'Erkak'), ('female', 'Ayol')]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    ACTIVITY_CHOICES = [
        ('student', 'Talaba'),
        ('employee', 'Xodim'),
        ('entrepreneur', 'Tadbirkor'),
    ]

    full_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    birth_date = models.DateField(null=True, blank=True)
    region = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    profession = models.CharField(max_length=150, blank=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.PositiveSmallIntegerField(null=True, blank=True)
    blood_glucose = models.FloatField(null=True, blank=True)
    bp_systolic = models.PositiveSmallIntegerField(null=True, blank=True)
    bp_diastolic = models.PositiveSmallIntegerField(null=True, blank=True)
    daily_steps = models.PositiveIntegerField(null=True, blank=True)
    sleep_hours = models.FloatField(null=True, blank=True)
    takes_medication = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    DIABETES_CHOICES = [('tip1', 'Tip 1'), ('tip2', 'Tip 2'), ('prediabet', 'Prediabet')]
    diabetes_type = models.CharField(max_length=20, choices=DIABETES_CHOICES, blank=True)
    risk_score = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or self.user.username

    @property
    def bmi(self):
        if not self.height_cm or not self.weight_kg:
            return None
        return round(self.weight_kg / (self.height_cm / 100) ** 2, 1)

    def calculate_risk_score(self):
        """
        Rule-based risk scoring (0–100). This is a deterministic hackathon
        placeholder — not a trained ML model. Each health marker contributes
        a weighted penalty; the sum is clamped to [0, 100].
        """
        score = 0

        # Blood glucose (normal < 5.6 mmol/L fasting)
        if self.blood_glucose is not None:
            if self.blood_glucose >= 11.1:
                score += 30
            elif self.blood_glucose >= 7.0:
                score += 20
            elif self.blood_glucose >= 5.6:
                score += 10

        # Blood pressure — systolic (normal < 120 mmHg)
        if self.bp_systolic is not None:
            if self.bp_systolic >= 180:
                score += 25
            elif self.bp_systolic >= 140:
                score += 15
            elif self.bp_systolic >= 130:
                score += 8
            elif self.bp_systolic >= 120:
                score += 4

        # Blood pressure — diastolic (normal < 80 mmHg)
        if self.bp_diastolic is not None:
            if self.bp_diastolic >= 120:
                score += 10
            elif self.bp_diastolic >= 90:
                score += 7
            elif self.bp_diastolic >= 80:
                score += 3

        # Physical inactivity (WHO: 10 000 steps/day target)
        if self.daily_steps is not None:
            if self.daily_steps < 3000:
                score += 15
            elif self.daily_steps < 5000:
                score += 10
            elif self.daily_steps < 8000:
                score += 5

        # Sleep (recommended 7–9 hours)
        if self.sleep_hours is not None:
            if self.sleep_hours < 5 or self.sleep_hours > 10:
                score += 10
            elif self.sleep_hours < 6 or self.sleep_hours > 9:
                score += 5

        # BMI
        bmi = self.bmi
        if bmi is not None:
            if bmi >= 35:
                score += 15
            elif bmi >= 30:
                score += 10
            elif bmi >= 25:
                score += 5

        # Current medication use suggests pre-existing condition
        if self.takes_medication:
            score += 10

        # Age
        if self.age is not None:
            if self.age >= 65:
                score += 15
            elif self.age >= 50:
                score += 10
            elif self.age >= 40:
                score += 5

        self.risk_score = min(score, 100)
        return self.risk_score

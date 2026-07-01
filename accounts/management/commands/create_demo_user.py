from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates the demo user (demo/demo12345) with a fully populated Profile.'

    def handle(self, *args, **options):
        from accounts.models import Profile

        # Demo user
        user, created = User.objects.get_or_create(username='demo')
        if created:
            user.set_password('demo12345')
            user.save()
            self.stdout.write('  Created user: demo')
        else:
            self.stdout.write('  User demo already exists — updating profile')

        from datetime import date
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.full_name        = 'Malika Karimova'
        profile.gender           = 'female'
        profile.birth_date       = date(1979, 3, 15)
        profile.age              = 47
        profile.phone_number     = '+998901234567'
        profile.region           = 'Toshkent shahri'
        profile.district         = 'Yunusobod tumani'
        profile.address          = 'Amir Temur ko\'chasi, 42-uy'
        profile.profession       = 'O\'qituvchi'
        profile.activity_type    = 'employee'
        profile.height_cm        = 164
        profile.weight_kg        = 82
        profile.blood_glucose    = 8.6   # mmol/L — diabetic range
        profile.bp_systolic      = 130
        profile.bp_diastolic     = 85
        profile.daily_steps      = 3200
        profile.sleep_hours      = 5.8
        profile.takes_medication = True
        profile.is_verified      = True
        profile.calculate_risk_score()
        profile.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'  Profile saved — risk_score={profile.risk_score}, BMI={profile.bmi}'
            )
        )

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Create demo doctors and patients'

    def handle(self, *args, **kwargs):
        doctors = [
            {'username': 'doctor1', 'password': 'Doctor123!', 'first_name': 'Sardor', 'last_name': 'Holmatov'},
            {'username': 'doctor2', 'password': 'Doctor123!', 'first_name': 'Nilufar', 'last_name': 'Qodirova'},
        ]
        for d in doctors:
            user, created = User.objects.get_or_create(username=d['username'])
            user.set_password(d['password'])
            user.first_name = d['first_name']
            user.last_name = d['last_name']
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.full_name = f"{d['first_name']} {d['last_name']}"
            profile.is_doctor = True
            profile.save()
            self.stdout.write(f"  Doctor {'created' if created else 'updated'}: {d['username']}")

        patients = [
            {
                'username': 'aziz', 'password': 'Patient123!',
                'first_name': 'Aziz', 'last_name': 'Karimov',
                'age': 45, 'diabetes_type': 'tip2',
                'blood_glucose': 12.4, 'bp_systolic': 145, 'bp_diastolic': 90,
            },
            {
                'username': 'malika', 'password': 'Patient123!',
                'first_name': 'Malika', 'last_name': 'Yusupova',
                'age': 32, 'diabetes_type': 'tip1',
                'blood_glucose': 8.1, 'bp_systolic': 120, 'bp_diastolic': 80,
            },
            {
                'username': 'jasur', 'password': 'Patient123!',
                'first_name': 'Jasur', 'last_name': 'Rahimov',
                'age': 58, 'diabetes_type': 'tip2',
                'blood_glucose': 6.2, 'bp_systolic': 130, 'bp_diastolic': 85,
            },
        ]
        for p in patients:
            user, created = User.objects.get_or_create(username=p['username'])
            user.set_password(p['password'])
            user.first_name = p['first_name']
            user.last_name = p['last_name']
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.full_name = f"{p['first_name']} {p['last_name']}"
            profile.is_doctor = False
            profile.age = p['age']
            profile.diabetes_type = p['diabetes_type']
            profile.blood_glucose = p['blood_glucose']
            profile.bp_systolic = p['bp_systolic']
            profile.bp_diastolic = p['bp_diastolic']
            profile.calculate_risk_score()
            profile.save()
            self.stdout.write(f"  Patient {'created' if created else 'updated'}: {p['username']}")

        self.stdout.write(self.style.SUCCESS('Done.'))

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from accounts.ml_service import predict_diabetes_risk, _model, _MODEL_PATH


class Command(BaseCommand):
    help = "Test the ML diabetes risk model against the demo user profile."

    def handle(self, *args, **options):
        User = get_user_model()

        self.stdout.write(f"Model path : {_MODEL_PATH}")
        self.stdout.write(f"Model loaded: {'YES' if _model else 'NO — falling back to rule-based'}\n")

        for username in ("demo", "aziz"):
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(f"User '{username}' not found, skipping.")
                continue

            profile = user.profile
            result = predict_diabetes_risk(profile)

            self.stdout.write(f"--- {username} ({profile.full_name}) ---")
            self.stdout.write(f"  glucose      : {profile.blood_glucose}")
            self.stdout.write(f"  bp_diastolic : {profile.bp_diastolic}")
            self.stdout.write(f"  bmi          : {profile.bmi}")
            self.stdout.write(f"  age          : {profile.age}")

            if result is None:
                self.stdout.write("  result       : None (blood_glucose not set — onboarding incomplete)")
            else:
                label = "DIABETIC RISK" if result["risk_class"] == 1 else "LOW RISK"
                self.stdout.write(
                    f"  ML result    : class={result['risk_class']} ({label}), "
                    f"risk={result['risk_percent']}%"
                )
            self.stdout.write("")

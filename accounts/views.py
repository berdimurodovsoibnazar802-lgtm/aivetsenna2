import re
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Profile

User = get_user_model()

_STEPPER_STEPS = ['Hisob yaratish', 'Ma\'lumotlaringiz', 'Tasdiqlash', 'Tayyor']


def _validate_password(pw):
    """Return list of error strings; empty list means valid."""
    errors = []
    if len(pw) < 8:
        errors.append('Parol kamida 8 ta belgidan iborat bo\'lishi kerak.')
    if not re.search(r'[A-Z]', pw):
        errors.append('Parolda kamida bitta katta harf bo\'lishi kerak.')
    if not re.search(r'[a-z]', pw):
        errors.append('Parolda kamida bitta kichik harf bo\'lishi kerak.')
    if not re.search(r'[0-9]', pw):
        errors.append('Parolda kamida bitta raqam bo\'lishi kerak.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/]', pw):
        errors.append('Parolda kamida bitta maxsus belgi bo\'lishi kerak.')
    return errors


def register_view(request):
    errors = {}
    post = request.POST if request.method == 'POST' else {}

    if request.method == 'POST':
        first_name   = post.get('first_name', '').strip()
        last_name    = post.get('last_name', '').strip()
        email        = post.get('email', '').strip()
        phone        = post.get('phone_number', '').strip()
        password     = post.get('password', '')
        password2    = post.get('password2', '')

        if not first_name:
            errors['first_name'] = 'Ism kiritilishi shart.'
        if not last_name:
            errors['last_name'] = 'Familiya kiritilishi shart.'
        if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors['email'] = 'To\'g\'ri e-mail manzil kiriting.'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Bu e-mail allaqachon ro\'yxatdan o\'tgan.'

        pw_errors = _validate_password(password)
        if pw_errors:
            errors['password'] = pw_errors[0]
        if password != password2:
            errors['password2'] = 'Parollar mos kelmaydi.'

        if not errors:
            username = email.split('@')[0]
            base, n = username, 1
            while User.objects.filter(username=username).exists():
                username = f'{base}{n}'; n += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            Profile.objects.create(
                user=user,
                full_name=f'{first_name} {last_name}',
                phone_number=f'+998{phone}',
            )
            login(request, user)
            return redirect('register_step2')

    ctx = {
        'errors': errors,
        'post': post,
        'stepper_steps': _STEPPER_STEPS,
        'current_step': 1,
    }
    return render(request, 'accounts/register.html', ctx)


@login_required
def register_step2_view(request):
    from datetime import date as _date
    profile, _ = Profile.objects.get_or_create(user=request.user)
    errors = {}

    if request.method == 'POST':
        p = request.POST

        # birth_date — safe parse, empty → None, bad format → inline error
        raw_bd = p.get('birth_date', '').strip()
        birth_date = None
        if raw_bd:
            try:
                from datetime import datetime
                birth_date = datetime.strptime(raw_bd, '%Y-%m-%d').date()
            except ValueError:
                errors['birth_date'] = 'Noto\'g\'ri sana formati (YYYY-MM-DD).'

        if not errors:
            profile.gender        = p.get('gender', profile.gender)
            profile.birth_date    = birth_date
            profile.region        = p.get('region', '').strip()
            profile.district      = p.get('district', '').strip()
            profile.address       = p.get('address', '').strip()
            profile.profession    = p.get('profession', '').strip()
            profile.activity_type = p.get('activity_type', '').strip()
            profile.save()
            return redirect('register_step3')

    ctx = {
        'profile': profile,
        'errors': errors,
        'post': request.POST if request.method == 'POST' else {},
        'stepper_steps': _STEPPER_STEPS,
        'current_step': 2,
        'uz_regions': [
            'Toshkent shahri', 'Toshkent viloyati', 'Samarqand viloyati',
            'Buxoro viloyati', "Farg'ona viloyati", 'Andijon viloyati',
            'Namangan viloyati', 'Qashqadaryo viloyati', 'Surxondaryo viloyati',
            'Jizzax viloyati', 'Sirdaryo viloyati', 'Navoiy viloyati',
            'Xorazm viloyati', "Qoraqalpog'iston Respublikasi",
        ],
    }
    return render(request, 'accounts/register_step2.html', ctx)


@login_required
def register_step3_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    error = None

    if request.method == 'POST':
        email_code = request.POST.get('email_code', '').replace(' ', '')
        phone_code = request.POST.get('phone_code', '').replace(' ', '')
        # TODO: replace with real SMS/email provider verification later
        if len(email_code) == 6 and email_code.isdigit() and len(phone_code) == 6 and phone_code.isdigit():
            profile.is_verified = True
            profile.save()
            return redirect('register_step4')
        error = 'Iltimos, har ikkala 6 xonali kodni to\'liq kiriting.'

    ctx = {
        'stepper_steps': _STEPPER_STEPS,
        'current_step': 3,
        'error': error,
        'user_email': request.user.email,
        'user_phone': profile.phone_number,
    }
    return render(request, 'accounts/register_step3.html', ctx)


@login_required
def register_step4_view(request):
    return render(request, 'accounts/register_step4.html', {
        'stepper_steps': _STEPPER_STEPS,
        'current_step': 4,
    })


def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password'),
        )
        if user is not None:
            login(request, user)
            try:
                if user.profile.is_doctor:
                    return redirect('doctor_dashboard')
            except Profile.DoesNotExist:
                pass
            return redirect('dashboard')
        messages.error(request, 'Noto\'g\'ri foydalanuvchi nomi yoki parol.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def onboarding_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        p = request.POST

        profile.full_name = p.get('full_name', '')
        profile.gender = p.get('gender', 'male')

        def _int(key):
            val = p.get(key)
            return int(val) if val else None

        def _float(key):
            val = p.get(key)
            return float(val) if val else None

        profile.age = _int('age')
        profile.height_cm = _int('height_cm')
        profile.weight_kg = _int('weight_kg')
        profile.blood_glucose = _float('blood_glucose')
        profile.bp_systolic = _int('bp_systolic')
        profile.bp_diastolic = _int('bp_diastolic')
        profile.daily_steps = _int('daily_steps')
        profile.sleep_hours = _float('sleep_hours')
        profile.takes_medication = p.get('takes_medication') == 'on'

        profile.calculate_risk_score()
        profile.save()
        return redirect('dashboard')

    return render(request, 'accounts/onboarding.html', {'profile': profile})


@login_required
def dashboard_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.calculate_risk_score()
    profile.save()

    current = profile.risk_score
    target = max(current - 25, 15)
    days = 30

    # Linear decline from current toward target over 30 days
    forecast_labels = [f'Kun {i + 1}' for i in range(days)]
    forecast_values = [
        round(current - (current - target) * (i / (days - 1)), 1)
        for i in range(days)
    ]

    context = {
        'profile': profile,
        'forecast_labels': forecast_labels,
        'forecast_values': forecast_values,
        'target': target,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def twin_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/twin.html', {'profile': profile})


@login_required
def analysis_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    risk_factors = []

    if profile.blood_glucose is not None and profile.blood_glucose >= 7.0:
        risk_factors.append({'name': 'Qon glyukozasi', 'level': 'high'})

    if profile.daily_steps is not None and profile.daily_steps < 6000:
        risk_factors.append({'name': 'Jismoniy faollik', 'level': 'medium'})

    if profile.sleep_hours is not None and profile.sleep_hours < 7:
        risk_factors.append({'name': 'Uyqu davomiyligi', 'level': 'medium'})

    if profile.takes_medication:
        risk_factors.append({'name': 'Dori qabul qilish', 'level': 'note'})

    context = {
        'profile': profile,
        'risk_factors': risk_factors,
    }
    return render(request, 'accounts/analysis.html', context)


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def health_medications_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    medications = [
        {
            'name': 'Metformin',
            'dosage': '500 mg',
            'frequency': '2×/kun (ertalab va kechqurun)',
            'since': '2022-03-15',
            'prescribed_by': 'Dr. Yusupov A.',
            'purpose': 'Qon shakarini pasaytirish (2-toifa diabet)',
            'status': 'Faol',
        },
        {
            'name': 'Lisinopril',
            'dosage': '10 mg',
            'frequency': '1×/kun (ertalab)',
            'since': '2023-01-08',
            'prescribed_by': 'Dr. Rashidova M.',
            'purpose': 'Qon bosimini nazorat qilish',
            'status': 'Faol',
        },
        {
            'name': 'Aspirin (kardiologik)',
            'dosage': '100 mg',
            'frequency': '1×/kun (ovqat bilan)',
            'since': '2023-01-08',
            'prescribed_by': 'Dr. Rashidova M.',
            'purpose': 'Yurak-tomir kasalliklari profilaktikasi',
            'status': 'Faol',
        },
    ]
    return render(request, 'accounts/health_medications.html', {
        'profile': profile,
        'medications': medications,
    })


@login_required
def health_labs_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    cbc = [
        {'name': 'Gemoglobin (Hb)',    'value': '11.2', 'unit': 'g/dL',     'ref': '12.0–16.0', 'status': 'low'},
        {'name': 'Eritrotsitlar (RBC)','value': '4.1',  'unit': '×10¹²/L',  'ref': '4.0–5.2',   'status': 'normal'},
        {'name': 'Leykotsitlar (WBC)', 'value': '9.8',  'unit': '×10⁹/L',   'ref': '4.5–11.0',  'status': 'normal'},
        {'name': 'Trombotsitlar',      'value': '412',  'unit': '×10⁹/L',   'ref': '150–400',   'status': 'high'},
        {'name': 'Gematokrit (Ht)',     'value': '34',   'unit': '%',         'ref': '36–46',     'status': 'low'},
        {'name': 'ESR',                'value': '28',   'unit': 'mm/soat',   'ref': '2–20',      'status': 'high'},
        {'name': 'CRP',                'value': '4.2',  'unit': 'mg/L',      'ref': '< 5.0',     'status': 'normal'},
    ]
    return render(request, 'accounts/health_labs.html', {
        'profile': profile,
        'cbc': cbc,
        'lab_date': '18.06.2026',
    })


@login_required
def health_twin_upgrade_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    organs = [
        {
            'name': 'Yurak',
            'detail': 'QB: 130/85 mmHg',
            'label': 'Kuzatuv talab qilinadi',
            'level': 'medium',
            'icon': 'heart',
        },
        {
            'name': "O'pka",
            'detail': "Ko'rsatkich me'yor doirasida",
            'label': 'Yaxshi holat',
            'level': 'low',
            'icon': 'lungs',
        },
        {
            'name': 'Jigar',
            'detail': "ALT, AST me'yor doirasida",
            'label': 'Yaxshi holat',
            'level': 'low',
            'icon': 'liver',
        },
        {
            'name': 'Buyrak',
            'detail': "Kreatinin me'yor doirasida",
            'label': 'Normal',
            'level': 'low',
            'icon': 'kidney',
        },
        {
            'name': 'Qon shakari',
            'detail': 'Glyukoza: 8.6 mmol/L',
            'label': 'Yuqori — shifokor bilan maslahatlashing',
            'level': 'high',
            'icon': 'glucose',
        },
    ]
    return render(request, 'accounts/health_twin_upgrade.html', {
        'profile': profile,
        'organs': organs,
    })


@login_required
def health_simulation_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    scenarios = [
        {
            'id': 'monitoring',
            'label': 'Faqat kuzatuv',
            'desc': "Dori yo'q, faqat muntazam tekshiruv",
            'risk_3m': 68,
            'risk_6m': 65,
            'risk_12m': 62,
            'color': '#FFB23B',
        },
        {
            'id': 'medication',
            'label': 'Dori qabul qilish',
            'desc': 'Metformin + Lisinopril davomi',
            'risk_3m': 52,
            'risk_6m': 45,
            'risk_12m': 40,
            'color': '#00D4FF',
        },
        {
            'id': 'combined',
            'label': 'Dori + turmush tarzi',
            'desc': "Dori + parhezkor ovqat + harakatlanish",
            'risk_3m': 42,
            'risk_6m': 32,
            'risk_12m': 24,
            'color': '#00FF88',
        },
    ]
    return render(request, 'accounts/health_simulation.html', {
        'profile': profile,
        'scenarios': scenarios,
    })


@login_required
def health_organs_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    organs = [
        {
            'name': 'Yurak',
            'detail': 'QB: 130/85 mmHg',
            'label': 'Kuzatuv talab qilinadi',
            'level': 'medium',
        },
        {
            'name': "O'pka",
            'detail': "Nafas olish me'yor doirasida",
            'label': 'Yaxshi holat',
            'level': 'low',
        },
        {
            'name': 'Jigar',
            'detail': "ALT/AST me'yor doirasida",
            'label': 'Normal',
            'level': 'low',
        },
        {
            'name': 'Buyrak',
            'detail': "Kreatinin me'yor doirasida",
            'label': 'Normal',
            'level': 'low',
        },
        {
            'name': 'Qon shakari',
            'detail': 'Glyukoza: 8.6 mmol/L',
            'label': 'Yuqori — shifokorga murojaat qiling',
            'level': 'high',
        },
    ]
    return render(request, 'accounts/health_organs.html', {
        'profile': profile,
        'organs': organs,
    })

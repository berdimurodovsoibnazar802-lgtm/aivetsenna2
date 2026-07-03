import json
import random
from datetime import date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from accounts.models import Profile
from accounts.ml_service import predict_diabetes_risk
from diabetes.models import DailyCheckIn, Alert


def _create_alerts(user, checkin):
    if checkin.glucose_fasting is not None:
        if checkin.glucose_fasting > 13.9:
            Alert.objects.create(user=user, alert_type='high_glucose',
                                 message='Qand darajasi xavfli yuqori')
        elif checkin.glucose_fasting < 3.9:
            Alert.objects.create(user=user, alert_type='low_glucose',
                                 message='Qand darajasi xavfli past')

    if checkin.bp_systolic is not None and checkin.bp_systolic > 160:
        Alert.objects.create(user=user, alert_type='high_bp',
                             message='Qon bosimi xavfli darajada yuqori')

    if checkin.medicine_taken is False:
        Alert.objects.create(user=user, alert_type='missed_medicine',
                             message='Dori qabul qilinmadi')

    if checkin.symptoms:
        count = len([s for s in checkin.symptoms.split(',') if s.strip()])
        if count >= 2:
            Alert.objects.create(user=user, alert_type='side_effects',
                                 message="Bir nechta nojo'ya ta'sir qayd etildi")


def _mock_timeline(seed):
    rng = random.Random(seed)
    today = date.today()
    rows = []
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        glucose = round(rng.uniform(6.0, 14.0), 1)
        bp_sys  = rng.randint(115, 160)
        bp_dia  = rng.randint(70, 100)
        taken   = rng.random() < 0.8
        symptom = rng.choice(['', '', '', '', 'Bosh aylanishi', 'Holsizlik', 'Uyquchanlik'])
        rows.append({
            'date':    d.strftime('%d.%m'),
            'glucose': glucose,
            'bp':      f"{bp_sys}/{bp_dia}",
            'taken':   taken,
            'symptom': symptom,
            'risk':    'high' if glucose > 11 else ('medium' if glucose >= 7 else 'low'),
        })
    return rows


def _doctor_required(request):
    if not request.user.is_authenticated:
        return False
    try:
        return request.user.profile.is_doctor
    except Profile.DoesNotExist:
        return False


def doctor_dashboard(request):
    if not _doctor_required(request):
        return redirect('login')
    patients = list(Profile.objects.filter(is_doctor=False).select_related('user'))
    for p in patients:
        ml = predict_diabetes_risk(p)
        p.ai_risk_percent = ml['risk_percent'] if ml else None
    patients.sort(key=lambda p: p.ai_risk_percent if p.ai_risk_percent is not None else -1, reverse=True)
    return render(request, 'doctor/dashboard.html', {'patients': patients})


def doctor_patient_detail(request, patient_id):
    if not _doctor_required(request):
        return redirect('login')
    patient = get_object_or_404(Profile, id=patient_id, is_doctor=False)
    ml = predict_diabetes_risk(patient)
    medicines = [
        {'name': 'Metformin', 'dosage': '500mg', 'status': 'Faol'},
        {'name': 'Aspirin',   'dosage': '100mg', 'status': 'Faol'},
    ]
    return render(request, 'doctor/patient_detail.html', {
        'patient': patient,
        'medicines': medicines,
        'ai_risk_percent': ml['risk_percent'] if ml else None,
        'ai_available': ml is not None,
    })


def doctor_simulation(request, patient_id):
    if not _doctor_required(request):
        return redirect('login')
    patient = get_object_or_404(Profile, id=patient_id, is_doctor=False)

    result = None
    form_data = {}

    if request.method == 'POST':
        form_data = request.POST
        med_class = request.POST.get('medicine_class', '')
        glucose   = patient.blood_glucose or 0
        bp        = patient.bp_systolic or 0
        age       = patient.age or 0

        # Decision rules
        if med_class == 'insulin' and glucose > 11:
            decision = 'green'
        elif med_class == 'metformin' and bp > 160:
            decision = 'yellow'
        elif med_class == 'metformin' and age > 70:
            decision = 'yellow'
        else:
            decision = 'green'

        # Hypoglycemia risk
        if med_class == 'insulin':
            hypo_risk = 'yuqori'
        elif med_class == 'sulfonilmochevina':
            hypo_risk = "o'rta"
        else:
            hypo_risk = 'past'

        result = {
            'decision': decision,
            'hypo_risk': hypo_risk,
        }

    return render(request, 'doctor/simulation.html', {
        'patient': patient,
        'result': result,
        'form_data': form_data,
    })


def doctor_timeline(request, patient_id):
    if not _doctor_required(request):
        return redirect('login')
    patient = get_object_or_404(Profile, id=patient_id, is_doctor=False)
    rows = _mock_timeline(seed=patient_id)

    labels        = json.dumps([r['date']    for r in rows])
    glucose_data  = json.dumps([r['glucose'] for r in rows])
    adherence_data = json.dumps([1 if r['taken'] else 0 for r in rows])

    return render(request, 'doctor/timeline.html', {
        'patient':        patient,
        'rows':           rows,
        'labels':         labels,
        'glucose_data':   glucose_data,
        'adherence_data': adherence_data,
    })


def patient_timeline(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        if request.user.profile.is_doctor:
            return redirect('doctor_dashboard')
    except Profile.DoesNotExist:
        pass

    rows = _mock_timeline(seed=request.user.id)
    labels         = json.dumps([r['date']    for r in rows])
    glucose_data   = json.dumps([r['glucose'] for r in rows])
    adherence_data = json.dumps([1 if r['taken'] else 0 for r in rows])

    return render(request, 'patient/timeline.html', {
        'rows':           rows,
        'labels':         labels,
        'glucose_data':   glucose_data,
        'adherence_data': adherence_data,
    })


def patient_checkin(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        if request.user.profile.is_doctor:
            return redirect('dashboard')
    except Profile.DoesNotExist:
        pass

    saved = False

    if request.method == 'POST':
        def intval(key):
            v = request.POST.get(key, '').strip()
            return int(v) if v else None

        def floatval(key):
            v = request.POST.get(key, '').strip()
            return float(v) if v else None

        taken_raw = request.POST.get('medicine_taken')
        medicine_taken = True if taken_raw == 'ha' else (False if taken_raw == 'yoq' else None)

        symptoms_list = request.POST.getlist('symptoms')
        symptoms_str  = ', '.join(symptoms_list)

        checkin = DailyCheckIn.objects.create(
            user             = request.user,
            date             = timezone.localdate(),
            glucose_fasting  = floatval('glucose_fasting'),
            glucose_postmeal = floatval('glucose_postmeal'),
            bp_systolic      = intval('bp_systolic'),
            bp_diastolic     = intval('bp_diastolic'),
            pulse            = intval('pulse'),
            weight_kg        = floatval('weight_kg'),
            medicine_name    = request.POST.get('medicine_name', '').strip(),
            medicine_taken   = medicine_taken,
            medicine_time    = request.POST.get('medicine_time') or None,
            skip_reason      = request.POST.get('skip_reason', '').strip(),
            breakfast         = request.POST.get('breakfast', '').strip(),
            lunch             = request.POST.get('lunch', '').strip(),
            dinner            = request.POST.get('dinner', '').strip(),
            physical_activity = request.POST.get('physical_activity', '').strip(),
            activity_duration = intval('activity_duration'),
            sleep_hours       = floatval('sleep_hours'),
            stress_level      = intval('stress_level'),
            symptoms          = symptoms_str,
            wellbeing_note    = request.POST.get('wellbeing_note', '').strip(),
        )
        _create_alerts(request.user, checkin)
        saved = True

    symptoms_list = [
        'Bosh aylanishi', 'Uyquchanlik', "Ko'ngil aynishi", 'Ishtaha pasayishi',
        "Qorin og'rig'i", 'Holsizlik', 'Terlash', "Qo'l titrashi",
        'Yurak tez urishi', "Hech qanday nojo'ya ta'sir yo'q",
    ]
    return render(request, 'patient/checkin.html', {'saved': saved, 'symptoms_list': symptoms_list})


def alerts_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    alerts     = Alert.objects.filter(user=request.user)
    unread_count = alerts.filter(is_read=False).count()
    return render(request, 'patient/alerts.html', {
        'alerts':       alerts,
        'unread_count': unread_count,
    })


def mark_alert_read(request, alert_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        Alert.objects.filter(id=alert_id, user=request.user).update(is_read=True)
    return redirect('alerts_view')

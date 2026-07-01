from django.urls import path
from . import views

urlpatterns = [
    path('',                                         views.doctor_dashboard,       name='doctor_dashboard'),
    path('patient/<int:patient_id>/',                views.doctor_patient_detail,  name='doctor_patient_detail'),
    path('patient/<int:patient_id>/simulation/',     views.doctor_simulation,      name='doctor_simulation'),
    path('patient/<int:patient_id>/timeline/',       views.doctor_timeline,        name='doctor_timeline'),
]

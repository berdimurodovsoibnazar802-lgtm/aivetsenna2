from django.contrib import admin
from django.urls import path, include
from diabetes import views as diabetes_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('doctor/', include('diabetes.urls')),
    path('checkin/',          diabetes_views.patient_checkin, name='patient_checkin'),
    path('patient/timeline/', diabetes_views.patient_timeline,  name='patient_timeline'),
    path('alerts/',           diabetes_views.alerts_view,       name='alerts_view'),
    path('alerts/<int:alert_id>/read/', diabetes_views.mark_alert_read, name='mark_alert_read'),
]

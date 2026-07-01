from django.urls import path
from . import views

urlpatterns = [
    path('register/',       views.register_view,       name='register'),
    path('register/step2/', views.register_step2_view, name='register_step2'),
    path('register/step3/', views.register_step3_view, name='register_step3'),
    path('register/step4/', views.register_step4_view, name='register_step4'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('',          views.dashboard_view,  name='dashboard'),
    path('twin/',     views.twin_view,     name='twin'),
    path('analysis/', views.analysis_view, name='analysis'),
    path('profile/',  views.profile_view,  name='profile'),
]

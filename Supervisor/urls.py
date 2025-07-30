from django.urls import path
from . import views

urlpatterns = [
    path('Supervisor_home', views.Supervisor_home, name='Supervisor_home'),
    path('Supervisor_jobcard', views.Supervisor_jobcard, name='Supervisor_jobcard'),
    path('jobcard_create_pg', views.Supervisor_jobcard_create_pg, name='jobcard_create_pg'),
    path('Supervisor_single_jobcard/<id>', views.Supervisor_single_jobcard, name='Supervisor_single_jobcard'),
    path('supervisor_view_stock', views.supervisor_view_stock, name='supervisor_view_stock'),
    path('profile', views.profile, name='Supervisorprofile'),

    path('supervisor_profileUpdate', views.supervisor_profileUpdate, name='supervisor_profileUpdate'),

    path('create-job-card/', views.create_job_card, name='create_job_card'),
    path('returnparts/', views.returnparts, name='returnparts'),
    path('update_job_card/', views.update_job_card, name='update_job_card'),
    path('record_payment/', views.record_payment, name='record_payment'),
    path('generate_invoice/', views.generate_invoice, name='generate_invoice'),
    # path('generate_invoice/', views.generate_invoice, name='generate_invoice'),



    path('attendance/', views.attendance_page, name='attendance_page'),
    path('attendance/api/', views.attendance_list, name='attendance_list'),
    path('attendance/api/<int:attendance_id>/', views.update_attendance, name='update_attendance'),

    path('supervisor_view_staff_attendance/', views.supervisor_view_staff_attendance, name='supervisor_view_staff_attendance'),
    
]

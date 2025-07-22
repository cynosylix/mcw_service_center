from django.urls import path
from . import views

urlpatterns = [
    path('Supervisor_home', views.Supervisor_home, name='Supervisor_home'),
    path('Supervisor_jobcard', views.Supervisor_jobcard, name='Supervisor_jobcard'),
    path('jobcard_create_pg', views.Supervisor_jobcard_create_pg, name='jobcard_create_pg'),
    path('Supervisor_single_jobcard/<id>', views.Supervisor_single_jobcard, name='Supervisor_single_jobcard'),
    path('supervisor_view_stock', views.supervisor_view_stock, name='supervisor_view_stock'),


    path('create-job-card/', views.create_job_card, name='create_job_card'),
    path('returnparts/', views.returnparts, name='returnparts'),
    path('update_job_card/', views.update_job_card, name='update_job_card'),

]
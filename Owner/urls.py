from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('OwnerHome', views.Owner_home, name='OwnerHome'),
    path('OwnerCustomerPg', views.OwnerCustomerPg, name='OwnerCustomerPg'),
    path('JobCardpg', views.JobCardpg, name='JobCardpg'),
    path('view_single_job/<id>', views.view_single_job, name='view_single_job'),
    path('ViewStaffPg', views.ViewStaffPg, name='ViewStaffPg'),
    path('StockPg', views.StockPg, name='StockPg'),
    path('Owner_jobcard_create_pg', views.Owner_jobcard_create_pg, name='Owner_jobcard_create_pg'),

    path('login_btn',views.login_btn),
    path('profile', views.profile, name='ownerprofile'),

    path('owner_profileUpdate', views.owner_profileUpdate, name='owner_profileUpdate'),
    path('owner_create_job_card/', views.owner_create_job_card, name='owner_create_job_card'),
    path('reminders', views.reminders, name='reminders'),


]
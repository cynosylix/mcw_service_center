from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('OwnerHome', views.Owner_home, name='OwnerHome'),
    path('OwnerCustomerPg', views.OwnerCustomerPg, name='OwnerCustomerPg'),
    path('JobCardpg', views.JobCardpg, name='JobCardpg'),
    path('view_single_job', views.view_single_job, name='view_single_job'),
    path('ViewStaffPg', views.ViewStaffPg, name='ViewStaffPg'),
    path('StockPg', views.StockPg, name='StockPg'),

    path('login_btn',views.login_btn),


    path('owner_attendance/', views.owner_attendance_page, name='attendance_page'),
    path('owner_attendance/api/', views.owner_attendance_list, name='attendance_list'),
    path('owner_attendance/api/<int:attendance_id>/', views.owner_update_attendance, name='update_attendance'),
]
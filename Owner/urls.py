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

    path('login_btn',views.login_btn),
]
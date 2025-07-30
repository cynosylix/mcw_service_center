from django.urls import path
from . import views

urlpatterns = [
    path('SparePurchase_home', views.SparePurchase_home, name='SparePurchase_home'),
    path('Attendance', views.Attendance, name='Attendance'),
    path('profile', views.profile, name='profile'),

    path('logout', views.logout),
    path('profileUpdate', views.profileUpdate, name='profileUpdate'),

    # ajax
    path('add_stock/', views.add_stock, name='add_stock'),
]
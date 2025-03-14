"""
URL configuration for fuser project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from fuser import views

urlpatterns = [
    path('user/', views.UserListView.as_view(), name='user-list'),
    path('user/<int:pk>', views.UserDetailView.as_view(), name='user-detail'),
    path('user/<int:pk>/update-verification', views.UserUpdateVerificationView.as_view(), name='user-update-verification'),
    path('user/<int:pk>/update-balance', views.UserUpdateBalanceView.as_view(), name='user-update-balance'),
]

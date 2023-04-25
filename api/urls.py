from django.urls import path, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from api import views

urlpatterns = [
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('signup/', views.Registration.as_view()),
    path('organization/create/', views.OrganizationCreate.as_view()),
    path('organizations/', views.Organizations.as_view()),
    re_path(r'^user/(?:pk=(?P<pk>[0-9]+)/)?$', views.UserView.as_view()),
    re_path(r'^user/edit/(?:pk=(?P<pk>[0-9]+)/)?$', views.UserEdit.as_view()),
    path('users/', views.Users.as_view())
]
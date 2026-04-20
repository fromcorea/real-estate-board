from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page=None), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('password/change/', PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url='/accounts/profile/'
    ), name='password_change'),
]

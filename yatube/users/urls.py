from django.contrib.auth import views as auth_view

from django.urls import path, reverse_lazy

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        views.LogOut.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'login/',
        views.LogIn.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change/',
        auth_view.PasswordChangeView.as_view(
            template_name='users/password_change_form.html',
            success_url=reverse_lazy('users:password_change_done')
        ),
        name='password_change'
    ),
    path(
        'password_change/done',
        auth_view.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        auth_view.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            success_url=reverse_lazy('users:password_reset_done')
        ),
        name='password_reset'
    ),
    path(
        'password_reset/done',
        auth_view.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>',
        auth_view.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_view.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]

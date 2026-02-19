import profile
from tkinter.font import names

from django.urls import path, reverse_lazy
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', register, name='register'),

    path('', user_login, name='login'),

    path('password-change/', auth_views.PasswordChangeView.as_view(success_url='done'), name='password_change'),

    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html',
                                                                 email_template_name='registration/password_reset_email.html',
                                                                 subject_template_name='registration/password_reset_subject.txt',
                                                                 html_email_template_name='registration/password_reset_email.html'
                                                                 ),
         name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),

    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('password_reset_complete'),
                                                     template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('logout/', user_logout, name='logout'),

    path('register/', register, name='register'),

    path('account/edit', edit_account, name='account_edit'),

    path('post/', post_list, name='post_list_page'),

    path('post/<str:category>',post_list, name='post_list_category'),

    path('post/<slug:slug>/', post_detail, name='post_detail_page'),

    path('author/<int:id>/',author,name='author'),

    path('ticket/', ticket, name='ticket'),

    path('post/<int:id>/comment/', post_comment, name='post_comment'),

    path('blog/', index, name="blog"),

    path('create-post/', creatpost, name='creat_post'),

    path('delete-post/<int:post_id>', delete_post, name='delete_post'),

    path('edit-post/<int:post_id>', edit_post, name='edit_post'),

    path('search/', post_search, name='post_search'),

    path('profile/', profile, name='profile'),
]

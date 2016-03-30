from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^login_redirect/', views.login_redirect, name='login_redirect'),
]

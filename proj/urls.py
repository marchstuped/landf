"""proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import include
from django.urls import path
import notifications.urls

from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pwa.urls')),
    path('',views.signIn),
    path('postsignin/',views.postsignin),
    path('logout/',views.logout,name = 'logout'),
    path('signup/',views.signUp,name = 'signup'),
    path('postsignup/',views.postsignup,name = 'postsignup'),
    path('create_lost/',views.create_lost,name = 'create_lost'),
    path('create_found/',views.create_found,name = 'create_found'),
    path('post_create_lost/',views.post_create_lost,name = 'post_create_lost'),
    path('post_create_found/',views.post_create_found,name = 'post_create_found'),
    path('check/',views.check,name = 'check'),
    path('post_check_L/',views.post_check_L,name = 'post_check_L'),
    path('post_check_F/',views.post_check_F,name = 'post_check_F'),
    path('post_check_on_L/',views.post_check_on_L,name = 'post_check_on_L'),
    path('post_check_on_F/',views.post_check_on_F,name = 'post_check_on_F'),
    path('post_check_on_we_L/',views.post_check_on_we_L,name = 'post_check_on_we_L'),
    path('post_check_on_we_F/',views.post_check_on_we_F,name = 'post_check_on_we_F'),
    path('match_post_L/',views.match_post_L,name = 'match_post_L'),
    path('match_post_F/',views.match_post_F,name = 'match_post_F'),
    path('history/',views.history,name = 'history'),
    path('^inbox/notifications/', include(notifications.urls, namespace='notifications')),

]

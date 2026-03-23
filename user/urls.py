from django.urls import path
from user.views.home import index



app_name = 'user'

urlpatterns = [
    
    # home
    path('', index, name='index'),


]
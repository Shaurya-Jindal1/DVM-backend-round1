from django.urls import path
from . import views

app_name = 'lastfm'

urlpatterns = [
    path('', views.home, name='home'),
    path('charts/', views.top_charts, name='charts'),
    path('search/', views.search, name='search'),
    path('artist/<str:name>/', views.artist_page, name='artist'),
    path('user/', views.find_user, name='find_user'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('user/<str:username>/weekly/', views.weekly_chart, name='weekly_chart'),
]

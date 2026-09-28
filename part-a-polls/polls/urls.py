from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path('create/', views.create_poll, name='create_poll'),
    path('mypolls/', views.my_polls, name='my_polls'),
    path('<int:question_id>/close/', views.close_poll, name='close_poll'),
    path('<int:question_id>/reopen/', views.reopen_poll, name='reopen_poll'),
    path('<int:question_id>/delete/', views.delete_poll, name='delete_poll'),
]

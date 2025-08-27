from django.urls import path
from . import views

urlpatterns = [
    path('', views.random_quote_view, name='random_quote'),
    path('popular/', views.popular_quotes_view, name='popular_quotes'),
    path('<int:quote_id>/like/', views.like_quote, name='like_quote'),
    path('<int:quote_id>/dislike/', views.dislike_quote, name='dislike_quote'),
    path('manage/', views.manage_quotes_view, name='manage_quotes'),
    path('<int:quote_id>/delete/', views.delete_quote, name='delete_quote'),
]
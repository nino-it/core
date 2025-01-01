
# File: myapp/urls.py
from django.urls import path
from . import views
# from .views import article_create_view

urlpatterns = [
    # path('', views.article_create_view, name='article_create'),
    path('calendar/', views.calendar_view, name='calendar'),    
    path('article/edit-or-create/', views.article_edit_or_create, name='article_edit_or_create'),
    path('article/delete/', views.article_delete, name='article_delete'),
    path('enter_bill/', views.enter_bill, name='enter_bill'),

    
    # path('article/create/', article_create_view, name='article_create'),
    # path('article/<int:article_id>/edit/', views.edit_article, name='edit_article'),

]

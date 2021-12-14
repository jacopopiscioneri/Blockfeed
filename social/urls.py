from django.urls import path
from . import views
from social.views import *

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('social/', numberOfPosts, name='number-posts'),
    path('profile/<int:pk>', ProfileView.as_view(), name='profile'),
    path('postLastHour', views.postLastHour, name='postLastHour'),
    path('search/', PostSearch.as_view(), name='post-search'),
    path('profile/edit/<int:pk>', ProfileEditView.as_view(), name='profile-edit'),

]

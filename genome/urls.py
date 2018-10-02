from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'genome'
urlpatterns = [
	url(r'^$', views.genome, name='genome'),
	path('boardgame/<int:bgg_id>/', views.boardgame_detail,
		 name='boardgame_detail'),
	url(r'^retrieve_recommendations/$', views.retrieve_recommendations,
		name='retrieve_recommendations'),
	url(r'^retrieve_user_collection/$', views.retrieve_user_collection,
		name='retrieve_user_collection'),
	path('user/<str:username>/<int:owned>/<int:rating>', views.user,
		name='user')
]
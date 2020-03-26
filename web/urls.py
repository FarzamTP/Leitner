from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('^home/$', views.home, name='home'),
    url('^home/get_category_color/$', views.retrieve_category_color, name='retrieve_category_color'),
    url('^add_new_flashcard/$', views.add_new_flashcard, name='add_new_flashcard'),
    path('home/<slug:category_name>/<int:lv>/<int:page>', views.category_page_render, name='category_page_render'),

]
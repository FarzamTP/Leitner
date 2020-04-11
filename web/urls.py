from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [

    # ===============================================BOT‌ URLS=========================================================

    url('^$', views.index, name='index'),
    url('^home/$', views.home, name='home'),
    url('^home/logout$', views.logout_user, name='logout_user'),
    url('^home/get_category_color/$', views.retrieve_category_color, name='retrieve_category_color'),
    url('^home/get_selected_user_categories/$', views.get_selected_user_categories,
        name='get_selected_user_categories'),
    url('^add_new_flashcard/$', views.add_new_flashcard, name='add_new_flashcard'),
    path('home/<slug:category_name>/<int:lv>/<int:page>', views.category_page_render, name='category_page_render'),

    # ===============================================BOT‌ URLS=========================================================

    url('^api/get_all_users_data/', views.BOT_get_all_users_data, name='BOT_get_all_users_data'),
]

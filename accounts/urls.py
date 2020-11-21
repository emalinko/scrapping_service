from django.urls import path

from accounts.views import login_view, logout_view, register_view, user_update_view, user_delete_view, \
        new_search_params_view

urlpatterns = [
        path('login/', login_view, name='login'),
        path('logout/', logout_view, name='logout'),
        path('registration_complete/', register_view, name='registration_complete'),
        path('register/', register_view, name='register'),
        path('update/', user_update_view, name='update'),
        path('delete/', user_delete_view, name='delete'),
        path('contact/', new_search_params_view, name='contact'),
]

from django.urls import path
from .views import UserRegistrationView, UserLoginView, logout_user,UserBankAccountUpdateView,PassWordUpdateView

 
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', UserBankAccountUpdateView.as_view(), name='profile' ),
    path('passchange/', PassWordUpdateView.as_view(), name='passchange' )
]
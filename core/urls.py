from django.urls import path
from .views import SignupView, LoginView, test_mongo
from .views import protected_view
from .views import generate_website


urlpatterns = [
    path("test/", test_mongo),
    path("signup/", SignupView.as_view()),
    path("login/", LoginView.as_view()),
    path("protected/", protected_view),
    path("generate-website/", generate_website),
]

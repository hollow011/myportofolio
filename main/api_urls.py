from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from main import api_views as views

app_name = "api"
urlpatterns = [
    path("auth/token/", obtain_auth_token, name="token-auth"),
    path("auth/logout/", views.api_logout, name="logout"),
    path("projects/", views.project_list, name="project-list"),
    path("projects/<uuid:project_id>/", views.project_detail, name="project-detail"),
    path("projects/<uuid:project_id>/star/", views.project_star, name="project-star"),
    path("education/", views.education_list, name="education-list"),
    path("education/<uuid:education_id>/", views.education_detail, name="education-detail"),
    path("education/<uuid:education_id>/star/", views.education_star, name="education-star"),
]

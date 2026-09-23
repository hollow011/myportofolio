from django.urls import path

from main.views import (
    register,
    login_user,
    logout_user,
    toggle_star,
    create_education,
    delete_education,
    get_education_json,
    get_experience_json,
    show_education,
    update_education,
    create_project,
    delete_project,
    get_projects_json,
    get_projects_xml,
    show_experience,
    show_main,
    show_project_detail,
    show_projects,
)

app_name = "main"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("projects/<uuid:project_id>/star/", toggle_star, name="toggle_star"),
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("education/", show_education, name="show_education"),
    path("education/add/", create_education, name="create_education"),
    path("education/<uuid:education_id>/edit/", update_education, name="update_education"),
    path("education/<uuid:education_id>/delete/", delete_education, name="delete_education"),
    path("api/education/", get_education_json, name="get_education_json"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/<uuid:project_id>/delete/", delete_project, name="delete_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("api/projects/xml/", get_projects_xml, name="get_projects_xml"),
    path(
        "projects/<uuid:project_id>/",
        show_project_detail,
        name="show_project_detail",
    ),
]

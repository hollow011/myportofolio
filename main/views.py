from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import prefetch_related_objects
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from main.forms import EducationForm, ProjectForm
from main.models import Education, Experience, Project


def show_main(request):
    context = {
        "name": "Mohammad Adzka Aulia",
        "npm": "2506657005",
        "study_program": "S1 Ilmu Komputer",
        "last_login": request.COOKIES.get("last_login", "No login cookie available"),
        "bio": (
            "CS student at Universitas Indonesia, familiar with multiple "
            "programming languages and frameworks, and has experience as a "
            "web developer."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Mohammad Adzka Aulia",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


@require_GET
def show_projects(request):
    # Tutorial 3 simulates consuming JSON. This is an in-process call, not HTTP.
    json_response = get_projects_json(request)
    projects = [item.object for item in serializers.deserialize(
        "json", json_response.content.decode("utf-8")
    )]
    # Deserialized objects do not retain the QuerySet's prefetch cache.
    prefetch_related_objects(projects, "starred_by")
    context = {
        "name": "Mohammad Adzka Aulia",
        "project_list": projects,
        "title_query": request.GET.get("title", "").strip(),
    }
    return render(request, "projects.html", context)


def show_project_detail(request, project_id):
    context = {
        "name": "Mohammad Adzka Aulia",
        "project": get_object_or_404(Project, pk=project_id),
    }
    return render(request, "project_detail.html", context)


def _filtered_projects(request):
    projects = Project.objects.prefetch_related("starred_by")
    title_query = request.GET.get("title", "").strip()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    return projects


@require_GET
def get_projects_json(request):
    return HttpResponse(
        serializers.serialize("json", _filtered_projects(request), use_natural_foreign_keys=True),
        content_type="application/json",
    )


@require_GET
def get_projects_xml(request):
    return HttpResponse(
        serializers.serialize("xml", _filtered_projects(request), use_natural_foreign_keys=True),
        content_type="application/xml",
    )


@require_http_methods(["GET", "POST"])
@login_required(login_url="main:login")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    form = ProjectForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project added successfully!")
        return redirect("main:show_projects")
    return render(request, "projects_form.html", {
        "name": "Mohammad Adzka Aulia",
        "form": form,
    })


@require_POST
@login_required(login_url="main:login")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, "Project deleted successfully!")
    return redirect("main:show_projects")


@require_GET
def get_education_json(request):
    education = Education.objects.all()
    institution_query = request.GET.get("institution", "").strip()
    if institution_query:
        education = education.filter(institution__icontains=institution_query)
    return HttpResponse(
        serializers.serialize("json", education), content_type="application/json"
    )


@require_GET
def get_experience_json(request):
    return HttpResponse(
        serializers.serialize("json", Experience.objects.order_by("-started_at", "id")),
        content_type="application/json",
    )


@require_GET
def show_education(request):
    # Required by Assignment 3: deserialize JSON before rendering the list.
    response = get_education_json(request)
    education = serializers.deserialize("json", response.content.decode("utf-8"))
    return render(request, "education.html", {
        "name": "Mohammad Adzka Aulia",
        "education_list": [item.object for item in education],
        "institution_query": request.GET.get("institution", "").strip(),
    })


def _education_form_response(request, education=None):
    """Share validation/rendering while preserving the instance during updates."""
    is_update = education is not None
    form = EducationForm(
        request.POST if request.method == "POST" else None, instance=education
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        action = "updated" if is_update else "added"
        messages.success(request, f"Education {action} successfully!")
        return redirect("main:show_education")
    return render(request, "education_form.html", {
        "name": "Mohammad Adzka Aulia",
        "form": form,
        "education": education,
        "is_update": is_update,
    })


@require_http_methods(["GET", "POST"])
@staff_member_required
def create_education(request):
    return _education_form_response(request)


@require_http_methods(["GET", "POST"])
@staff_member_required
def update_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    return _education_form_response(request, education)


@require_POST
@staff_member_required
def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    education.delete()
    messages.success(request, "Education deleted successfully!")
    return redirect("main:show_education")


@require_http_methods(["GET", "POST"])
def register(request):
    form = UserCreationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("main:login")
    return render(request, "register.html", {
        "name": "Mohammad Adzka Aulia", "form": form,
    })


@require_http_methods(["GET", "POST"])
def login_user(request):
    form = AuthenticationForm(request, data=request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        # The tutorial returns to the profile; never trust an arbitrary next URL.
        response = redirect("main:show_main")
        response.set_cookie(
            "last_login", timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"),
            httponly=True, samesite="Lax", secure=request.is_secure(),
        )
        return response
    return render(request, "login.html", {
        "name": "Mohammad Adzka Aulia", "form": form,
    })


@require_POST
def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login", samesite="Lax")
    return response


@require_POST
@login_required(login_url="main:login")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    return redirect("main:show_projects")

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from main.forms import EducationForm, ProjectForm
from main.models import Education, Experience, Project
from main.permissions import education_access


def show_main(request):
    context = {
        "name": "Mohammad Adzka Aulia",
        "npm": "2506657005",
        "study_program": "S1 Ilmu Komputer",
        "last_login": request.COOKIES.get("last_login", "No login cookie available"),
        "featured_projects": Project.objects.all()[:3],
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
    context = {
        "name": "Mohammad Adzka Aulia",
        "form": ProjectForm(),
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
@never_cache
def get_projects_json(request):
    data = []
    for project in _filtered_projects(request):
        users = list(project.starred_by.all())
        data.append({
            "model": "main.project", "pk": str(project.pk),
            "fields": {
                "title": project.title, "description": project.description,
                "technology": project.technology,
                "repository_url": project.repository_url,
                "project_image_url": project.project_image_url,
                "is_featured": project.is_featured,
                "star_count": len(users),
                "is_starred": request.user.is_authenticated and any(
                    user.pk == request.user.pk for user in users
                ),
                "starred_by_names": ", ".join(user.username for user in users),
            },
        })
    return JsonResponse(data, safe=False)


@require_POST
def create_project_ajax(request):
    if not request.user.is_active or not request.user.is_superuser:
        return JsonResponse({"message": "Only the portfolio owner can add projects."}, status=403)
    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse({"message": "Project added successfully!", "pk": str(project.pk)}, status=201)
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


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
@never_cache
def get_education_json(request):
    """Public data plus session-specific star state; never serialize whole users."""
    education = Education.objects.prefetch_related("starred_by")
    institution_query = request.GET.get("institution", "").strip()
    if institution_query:
        education = education.filter(institution__icontains=institution_query)
    data = []
    for entry in education:
        users = list(entry.starred_by.all())
        data.append({
            "model": "main.education", "pk": str(entry.pk),
            "fields": {
                "institution": entry.institution, "degree": entry.degree,
                "degree_display": entry.get_degree_display(),
                "field_of_study": entry.field_of_study,
                "description": entry.description, "website": entry.website,
                "is_current": entry.is_current, "created_at": entry.created_at,
                "star_count": len(users),
                "is_starred": request.user.is_authenticated and any(
                    user.pk == request.user.pk for user in users
                ),
                "starred_by_names": ", ".join(user.username for user in users),
            },
        })
    return JsonResponse(data, safe=False)


@require_GET
def get_experience_json(request):
    return HttpResponse(
        serializers.serialize("json", Experience.objects.order_by("-started_at", "id")),
        content_type="application/json",
    )


@require_GET
def show_education(request):
    # Assignment 5 replaces the in-process JSON round trip with browser Fetch.
    return render(request, "education.html", {
        "name": "Mohammad Adzka Aulia",
        "form": EducationForm(),
        "institution_query": request.GET.get("institution", "").strip(),
        **education_access(request.user),
    })


@require_POST
def create_education_ajax(request):
    """Return JSON failures instead of redirecting Fetch to an HTML login page."""
    if not education_access(request.user)["can_create_education"]:
        return JsonResponse({"message": "Only the portfolio owner can add education."}, status=403)
    form = EducationForm(request.POST)
    if form.is_valid():
        education = form.save()
        return JsonResponse({
            "message": "Education added successfully!", "pk": str(education.pk),
        }, status=201)
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@require_GET
def show_education_detail(request, education_id):
    education = get_object_or_404(
        Education.objects.prefetch_related("starred_by"), pk=education_id
    )
    return render(request, "education_detail.html", {
        "name": "Mohammad Adzka Aulia", "education": education,
        **education_access(request.user),
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
@login_required(login_url="main:login")
def create_education(request):
    if not education_access(request.user)["can_create_education"]:
        raise PermissionDenied
    return _education_form_response(request)


@require_http_methods(["GET", "POST"])
@login_required(login_url="main:login")
def update_education(request, education_id):
    if not education_access(request.user)["can_edit_education"]:
        raise PermissionDenied
    education = get_object_or_404(Education, pk=education_id)
    return _education_form_response(request, education)


@require_POST
@login_required(login_url="main:login")
def delete_education(request, education_id):
    if not education_access(request.user)["can_delete_education"]:
        raise PermissionDenied
    education = get_object_or_404(Education, pk=education_id)
    education.delete()
    messages.success(request, "Education deleted successfully!")
    return redirect("main:show_education")


@require_POST
@login_required(login_url="main:login")
def toggle_education_star(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    # Identity always comes from the session, never a submitted user ID.
    if education.starred_by.filter(pk=request.user.pk).exists():
        education.starred_by.remove(request.user)
    else:
        education.starred_by.add(request.user)
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

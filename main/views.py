from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from main.forms import ProjectForm
from main.models import Experience, Project


def show_main(request):
    context = {
        "name": "Mohammad Adzka Aulia",
        "npm": "2506657005",
        "study_program": "S1 Ilmu Komputer",
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
    projects = serializers.deserialize("json", json_response.content.decode("utf-8"))
    context = {
        "name": "Mohammad Adzka Aulia",
        "project_list": [project.object for project in projects],
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
    projects = Project.objects.all()
    title_query = request.GET.get("title", "").strip()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    return projects


@require_GET
def get_projects_json(request):
    return HttpResponse(
        serializers.serialize("json", _filtered_projects(request)),
        content_type="application/json",
    )


@require_GET
def get_projects_xml(request):
    return HttpResponse(
        serializers.serialize("xml", _filtered_projects(request)),
        content_type="application/xml",
    )


@require_http_methods(["GET", "POST"])
def create_project(request):
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
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, "Project deleted successfully!")
    return redirect("main:show_projects")

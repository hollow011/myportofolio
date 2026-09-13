from django.shortcuts import get_object_or_404, render

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


def show_projects(request):
    context = {
        "name": "Mohammad Adzka Aulia",
        "project_list": Project.objects.all(),
    }
    return render(request, "projects.html", context)


def show_project_detail(request, project_id):
    context = {
        "name": "Mohammad Adzka Aulia",
        "project": get_object_or_404(Project, pk=project_id),
    }
    return render(request, "project_detail.html", context)

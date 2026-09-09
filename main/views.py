from django.shortcuts import render

from main.models import Experience


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

# Create your views here.

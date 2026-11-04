from django.db import transaction
from django.db.models import prefetch_related_objects
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Education, Project
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly, IsPortfolioOwnerOrReadOnly
from main.serializers import EducationSerializer, ProjectSerializer


def _list(request, queryset, serializer_class, search_field):
    context = {"request": request}
    if request.method in ("GET", "HEAD"):
        query = request.query_params.get(search_field, "").strip()
        if query:
            queryset = queryset.filter(**{f"{search_field}__icontains": query})
        return Response(serializer_class(queryset.prefetch_related("starred_by"), many=True, context=context).data)
    serializer = serializer_class(data=request.data, context=context)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def _detail(request, model, pk, serializer_class):
    entry = get_object_or_404(model.objects.prefetch_related("starred_by"), pk=pk)
    context = {"request": request}
    if request.method in ("GET", "HEAD"):
        return Response(serializer_class(entry, context=context).data)
    if request.method == "DELETE":
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = serializer_class(entry, data=request.data, partial=request.method == "PATCH", context=context)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@transaction.atomic
def _toggle_star(request, model, pk, serializer_class):
    # Concurrent toggles of the same production record must observe each other.
    entry = get_object_or_404(model.objects.select_for_update(), pk=pk)
    if entry.starred_by.filter(pk=request.user.pk).exists():
        entry.starred_by.remove(request.user)
    else:
        entry.starred_by.add(request.user)
    prefetch_related_objects([entry], "starred_by")
    return Response(serializer_class(entry, context={"request": request}).data)


@never_cache
@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    return _list(request, Project.objects.order_by("title", "id"), ProjectSerializer, "title")


@never_cache
@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_detail(request, project_id):
    return _detail(request, Project, project_id, ProjectSerializer)


@never_cache
@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    return _toggle_star(request, Project, project_id, ProjectSerializer)


@never_cache
@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_list(request):
    return _list(request, Education.objects.all(), EducationSerializer, "institution")


@never_cache
@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_detail(request, education_id):
    return _detail(request, Education, education_id, EducationSerializer)


@never_cache
@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def education_star(request, education_id):
    return _toggle_star(request, Education, education_id, EducationSerializer)

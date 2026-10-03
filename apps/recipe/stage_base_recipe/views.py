#/home/marcio/Desktop/projetos/app_prod_lve/apps/recipe/stage_base_recipe/views.py
from rest_framework import viewsets

from .models import StageBaseRecipe
from .serializers import StageBaseRecipeSerializer


class StageBaseRecipeViewSet(viewsets.ModelViewSet):
    queryset = StageBaseRecipe.objects.all()
    serializer_class = StageBaseRecipeSerializer
    filterset_fields = ("active",)
    search_fields = ("stage_base_recipe",)
    ordering_fields = ("stage_base_recipe",)

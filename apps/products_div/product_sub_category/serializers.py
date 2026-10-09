from rest_framework import serializers

from .models import ProductSubCategory


class ProductSubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.category", read_only=True)

    class Meta:
        model = ProductSubCategory
        fields = (
            "id",
            "sub_category",
            "category",
            "category_name",
            "markup_default",
            "description_menu",
            "active",
        )
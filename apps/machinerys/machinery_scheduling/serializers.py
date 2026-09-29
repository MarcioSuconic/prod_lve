from rest_framework import serializers

from .models import MachineryScheduling


class MachinerySchedulingSerializer(serializers.ModelSerializer):
    machinery_name = serializers.CharField(source="machinery.machinery", read_only=True)

    class Meta:
        model = MachineryScheduling
        fields = (
            "id",
            "machinery",
            "machinery_name",
            "datetime_initial",
            "datetime_finish",
            "register_production_sub_product",
            "active",
        )

    def validate(self, attrs):
        initial = attrs.get("datetime_initial", getattr(self.instance, "datetime_initial", None))
        finish = attrs.get("datetime_finish", getattr(self.instance, "datetime_finish", None))
        if initial and finish and finish <= initial:
            raise serializers.ValidationError(
                {"datetime_finish": "Deve ser posterior ao horário inicial."}
            )
        return attrs
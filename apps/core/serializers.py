from rest_framework import serializers

from .models import SiteConfiguration


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteConfiguration
        fields = [
            "site_name",
            "logo",
            "contact_email",
            "footer_text",
            "max_images_per_ad",
            "updated_at",
        ]


class LimitsSerializer(serializers.Serializer):
    image_max = serializers.IntegerField()
    text_limits = serializers.DictField(child=serializers.IntegerField())

from rest_framework.serializers import ModelSerializer
from .models import CompanySocials, DealsBanner


class CompanySocialsSerializer(ModelSerializer):
    class Meta:
        model = CompanySocials
        exclude = ('id', )

class DealsBannerSerializer(ModelSerializer):
    class Meta:
        model = DealsBanner
        fields = "__all__"

from .models import ColorMarker, Order
from rest_framework.serializers import ModelSerializer, JSONField, IntegerField
from .image_converter import create_marker


class ColorMarkerSerializer(ModelSerializer):

    def create(self, validated_data):
        validated_data["image"] = create_marker(validated_data["color"])
        return super(ColorMarkerSerializer, self).create(validated_data)

    class Meta:
        fields = '__all__'
        model = ColorMarker


class OrderSerializer(ModelSerializer):

    user_details = JSONField(source="get_user_details", read_only=True)
    color_marker_details = JSONField(source="get_color_marker_details", read_only=True)
    rank = IntegerField(source="get_rank", read_only=True)
    not_archived_rank = IntegerField(source="get_not_archived_rank", read_only=True)

    class Meta:
        fields = '__all__'
        model = Order

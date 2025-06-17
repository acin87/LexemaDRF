from rest_framework import serializers


class GalleryImageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    src = serializers.ImageField()
    uploaded_at = serializers.DateTimeField()
    uploaded_by = serializers.IntegerField()
    image_width = serializers.IntegerField()
    image_height = serializers.IntegerField()
    image_size = serializers.IntegerField()
    source_type = serializers.CharField()
    source_id = serializers.IntegerField()
    post_id = serializers.IntegerField()

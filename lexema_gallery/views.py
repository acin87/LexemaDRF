from datetime import timedelta


from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lexema_comment.models import CommentImages
from lexema_gallery.serializers import GalleryImageSerializer
from lexema_post.models import PostImage
from PIL import Image
from io import BytesIO
import os


# Create your views here.
class GalleryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        days = int(request.query_params.get("days", 30))
        limit = int(request.query_params.get("limit", 50))

        date_from = timezone.now() - timedelta(days=days)

        post_images = PostImage.objects.filter(
            uploaded_by=user, uploaded_at__gte=date_from
        ).select_related("post", "uploaded_by")

        comment_images = CommentImages.objects.filter(
            uploaded_by=user, uploaded_at__gte=date_from
        ).select_related("comment__post", "uploaded_by")

        gallery = []

        for img in post_images:
            try:
                with Image.open(img.image) as pil_img:
                    width, height = pil_img.size
            except:
                width, height = None, None

            gallery.append(
                {
                    "id": img.id,
                    "src": request.build_absolute_uri(img.image.url),
                    "uploaded_at": img.uploaded_at,
                    "source_type": "post",
                    "source_id": img.post.id,
                    "post_id": img.post.id,
                    "width": width,
                    "height": height,
                    "size_kb": (
                        round(os.path.getsize(img.image.path) / 1024, 2)
                        if img.image
                        else None
                    ),
                    "aspect_ratio": (
                        round(width / height, 2) if width and height else None
                    ),
                }
            )

        for img in comment_images:
            try:
                with Image.open(img.image) as pil_img:
                    width, height = pil_img.size
            except:
                width, height = None, None

            gallery.append(
                {
                    "id": img.id,
                    "src": request.build_absolute_uri(img.image.url),
                    "uploaded_at": img.uploaded_at,
                    "source_type": "comment",
                    "source_id": img.comment.id,
                    "post_id": img.comment.post.id,
                    "width": width,
                    "height": height,
                    "size_kb": (
                        round(os.path.getsize(img.image.path) / 1024, 2)
                        if img.image
                        else None
                    ),
                    "aspect_ratio": (
                        round(width / height, 2) if width and height else None
                    ),
                }
            )

        gallery.sort(key=lambda x: x["uploaded_at"], reverse=True)

        gallery = gallery[:limit]

        return Response(
            {
                "count": len(gallery),
                "results": gallery,
                "meta": {
                    "requested_by": user.username,
                    "time_period": f"Last {days} days",
                    "image_count": {
                        "posts": len(post_images),
                        "comments": len(comment_images),
                        "total": len(post_images) + len(comment_images),
                    },
                },
            }
        )

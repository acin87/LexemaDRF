from rest_framework import viewsets

from lexema_app.models.profiles.Profile import Profiles
from lexema_app.serializers.friends import ProfilesSerializers


class ProfilesViewSet(viewsets.ModelViewSet):
    """Модель для списка друзей"""

    queryset = Profiles.objects.all().order_by(  # pylint: disable=no-member
        "-created_at"
    )
    serializer_class = ProfilesSerializers

from rest_framework import serializers

from lexema_app.models.profiles.Profile import Profiles



class ProfilesSerializers(serializers.ModelSerializer):

    

    class Meta:
        model = Profiles
        fields = ('id', 'name', 'email', 'created_at')
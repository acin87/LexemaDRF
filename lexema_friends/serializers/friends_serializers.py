from rest_framework import serializers
from lexema_friends.models import Friends



class FriendsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Friends
        fields = '__all__'
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    # password = serializers.Field(write_only=True)

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data['email'].encode('ascii')
        instance.username = validated_data['username'].encode('ascii')
        instance.first_name = validated_data['first_name'].encode('ascii')
        instance.last_name = validated_data['last_name'].encode('ascii')
        

        if validated_data.get('password', None):
            instance.set_password(validated_data['password'].encode('ascii'))
        instance.save()
        return instance

    class Meta:
        fields = '__all__'
        model = User

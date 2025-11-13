# file: dadjokes/serializer.py
# this file explains how to turn django data models into json files
from rest_framework import serializers
from .models import Joke, Picture


class JokeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Joke
        fields = ["id", "text", "contributor_name", "created_at"]


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ["id", "image_url", "contributor_name", "created_at"]

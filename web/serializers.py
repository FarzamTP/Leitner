from .models import FlashCart, Category, UserProfile
from rest_framework import serializers


class FlashCartSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FlashCart
        fields = ['category', 'word', 'definition', 'synonyms', 'example', 'lv']


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ['owner', 'name', 'color', 'number_of_flashcards', 'number_of_lv1',
                  'number_of_lv2', 'number_of_lv3', 'number_of_lv4', 'number_of_lv5']


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user']

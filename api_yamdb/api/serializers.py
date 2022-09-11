from datetime import datetime
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer."""
    class Meta:
        fields = ('name', 'slug',)
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Genre serializer."""
    class Meta:
        fields = ('name', 'slug',)
        model = Genre
        lookup_field = 'slug'


class TitlePostPatchSerializer(serializers.ModelSerializer):
    """Title patch & post serializer."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        year = datetime.today().year
        if year < value:
            raise serializers.ValidationError('Проверьте год выпуска!')
        return value


class TitleSerializer(serializers.ModelSerializer):
    """Title serializer."""
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.FloatField()

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Review serializer."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate_score(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError('Неверный рейтинг')
        return value

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title_id = self.context['view'].kwargs.get('id')
        title = get_object_or_404(Title, pk=title_id)
        user = self.context['request'].user
        if Review.objects.filter(title=title, author=user).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв к этому произведению'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class UserRegSerializer(serializers.Serializer):
    """User registration serializer."""
    email = serializers.EmailField(
        max_length=254,
        required=True
    )
    username = serializers.RegexField(
        max_length=150,
        required=True,
        regex=r'^[\w.@+-]'
    )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Имя не может быть "me".')
        return value

    class Meta:
        fields = ('username', 'email')
        model = User


class TokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        max_length=150,
        required=True,
        regex=r'^[\w.@+-]'
    )
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""
    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User

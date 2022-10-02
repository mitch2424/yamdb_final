from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ParseError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title
from users.models import User

from api_yamdb.settings import DEFAULT_FROM_EMAIL

from .filters import TitleFilter
from .mixins import CreateListDestroyMixins
from .permissions import IsAdministrator, IsOwnerOrReadOnly, IsReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitlePostPatchSerializer, TitleSerializer,
                          TokenSerializer, UserRegSerializer, UserSerializer)

SUBJECT = 'YaMDb: код подверждения'
MESSAGE = 'Ваш код подтверждения - {}'
FIELD_ERROR = 'Неуникальное поле. Пользователь с таким {} уже существует'


class CreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    class Meta:
        abstract = True


def get_object_or_400(model, **kwargs):
    try:
        model.objects.get(**kwargs)
    except Exception as error:
        raise ParseError(error)


class CategoryViewSet(CreateListDestroyMixins):
    """Вьюсет  Categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyMixins):
    """Вьюсет  Genres."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет Titles."""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('id')
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'category', 'genre')
    pagination_class = PageNumberPagination
    permission_classes = (IsAdministrator,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitlePostPatchSerializer
        return TitleSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsReadOnly(),)
        return super().get_permissions()


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    permission_classes = (IsAdministrator,)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me')
    def get_current_user_info(self, request):
        serializer = UserSerializer(request.user)
        if 'role' in request.data:
            return Response(serializer.data,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет Reviews."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (IsReadOnly(),)
        return super().get_permissions()

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['id'])
        return title.reviews.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет Comments."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (IsReadOnly(),)
        return super().get_permissions()

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(
            Review, pk=self.kwargs.get('id'),
            title__id=title_id
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(
                Review, pk=self.kwargs.get('id'),
                title__id=title_id)
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """Вьюсет user register."""
    serializer = UserRegSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user, created = User.objects.get_or_create(
            email=serializer.validated_data['email'],
            username=serializer.validated_data['username'],
        )
    except IntegrityError as error:
        return Response(f'{error}', status=status.HTTP_400_BAD_REQUEST)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        SUBJECT,
        MESSAGE.format(confirmation_code),
        DEFAULT_FROM_EMAIL,
        [user.email],
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username'],
    )
    if not default_token_generator.check_token(
            user,
            serializer.validated_data['confirmation_code']):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    token = AccessToken.for_user(user)
    data = {
        'token': str(token),
    }
    return Response(data)

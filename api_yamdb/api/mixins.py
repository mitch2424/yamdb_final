from rest_framework import mixins, viewsets, filters
from rest_framework.pagination import PageNumberPagination

from .permissions import IsAdministrator, IsReadOnly


class CreateListDestroyMixins(mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name',)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    permission_classes = (IsAdministrator,)

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsReadOnly(),)
        return super().get_permissions()

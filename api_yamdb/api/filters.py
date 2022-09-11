from django_filters import CharFilter, FilterSet

from reviews.models import Title


class TitleFilter(FilterSet):
    """Кастомный фильтр для Title. Жанры и категории по slug."""
    name = CharFilter(field_name='name', lookup_expr='contains')
    genre = CharFilter(field_name='genre__slug')
    category = CharFilter(field_name='category__slug')

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre')

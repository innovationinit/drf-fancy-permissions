from fancy_permissions import (
    model_action_permission_factory,
    object_action_permission_factory,
    parent_object_action_permission_factory,
)
from rest_framework.viewsets import ModelViewSet

from .models import Book
from .serializers import BookSerializer


class BookAPIView(ModelViewSet):

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [
        model_action_permission_factory(
            create=['testapp.add_book'],
            list=['testapp.change_book'],
            retrieve=['testapp.change_book'],
            destroy=['testapp.delete_book'],
            update=['testapp.change_book'],
            partial_update=['testapp.change_book'],
        )
    ]


book_view = BookAPIView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
    'post': 'create',
})


class BookListAPIView(ModelViewSet):

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [
        model_action_permission_factory(
            list=None,
        )
    ]


book_list_view = BookListAPIView.as_view({
    'get': 'list',
})


class SpecialBookAPIView(ModelViewSet):

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [
        object_action_permission_factory(
            retrieve=[lambda obj, user: obj.title.startswith('Special')],
            update=[lambda obj, user: obj.title.startswith('Special'), ],
        ),
        parent_object_action_permission_factory(
            retrieve=None,
            update=[lambda obj, user: obj.first_name == 'John']
        )
    ]

    def get_parent_object(self):
        return self.get_object().author


special_book_view = SpecialBookAPIView.as_view({
    'get': 'retrieve',
    'put': 'update',
})

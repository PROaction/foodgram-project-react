from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import User
from recipes.paginators import StandardResultsSetPagination
from users.serializers import (
    PasswordChangeSerializer,
    SubscriberSerializer,
    UserListSerializer,
    UserRegistrationSerializer, ReadUserSerializer,
)


class UserViewSet(BaseUserViewSet):
    serializer_class = UserListSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer

        if self.action == 'set_password':
            return PasswordChangeSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['id'])

        serializer = UserListSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'password set'})

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, *args, **kwargs):
        user = self.get_object()
        if request.method == 'POST':
            if user.id == request.user.id:
                return Response(
                    {'detail': 'Нельзя подписываться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if request.user.subscriptions.filter(id=user.id).exists():
                return Response(
                    {'detail': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            request.user.subscriptions.add(user)
            serializer = SubscriberSerializer(
                user, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if request.user.subscriptions.filter(id=user.id).exists():
                request.user.subscriptions.remove(user)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'detail': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        if request.method == 'GET':
            subscriptions = request.user.subscriptions.all()

            paginator = StandardResultsSetPagination()
            paginate_queryset = paginator.paginate_queryset(
                subscriptions, request
            )

            serializer = SubscriberSerializer(
                paginate_queryset, many=True, context={'request': request}
            )
            return paginator.get_paginated_response(serializer.data)

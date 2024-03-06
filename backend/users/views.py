from rest_framework import viewsets
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import UserListSerializer, UserRegistrationSerializer, PasswordChangeSerializer


class UserViewSet(BaseUserViewSet):
    serializer_class = UserListSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action == 'set_password':
            return PasswordChangeSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'password set'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        user = self.get_object()
        request.user.subscriptions.add(user)
        return Response({'status': 'subscribed'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unsubscribe(self, request, pk=None):
        user = self.get_object()
        request.user.subscriptions.remove(user)
        return Response({'status': 'unsubscribed'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = request.user.subscriptions.all()
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)

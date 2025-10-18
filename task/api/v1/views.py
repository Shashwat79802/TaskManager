from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from ...models import Task
from .serializers import TaskSerializer, RegisterSerializer
from ...permissions import IsOwnerOrAdminOrReadOnly


class TaskViewSet(viewsets.ModelViewSet):

    queryset = Task.objects.select_related('owner').all()
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['completed', 'owner__username']
    search_fields = ['title', 'description']
    ordering_fields = ['id', 'created_at', 'updated_at']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer
    permission_classes = []

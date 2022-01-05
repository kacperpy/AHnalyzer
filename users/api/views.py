from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from users.api.serializers import CustomUserSerializer
from rest_framework import viewsets, status
from users.models import CustomUser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cur_user_id = self.request.user.pk
        return [CustomUser.objects.get(pk=cur_user_id)]

class RealmSetAPIView(APIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, realm_id):
        user = request.user
        user.realm_id = realm_id
        user.save()
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
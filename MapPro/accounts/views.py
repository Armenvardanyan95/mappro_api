from rest_framework.viewsets import ModelViewSet, ViewSet
from .serializers import UserSerializer, User
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY
import json
from rest_framework.authtoken.views import ObtainAuthToken, Token


class UserViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthenticated,)


class UserDelete(ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        body = json.loads(request.body.decode('utf-8'))
        if not request.user.check_password(body["password"]):
            return Response(status=HTTP_422_UNPROCESSABLE_ENTITY, data={"message": 'Password not correct'})
        User.objects.filter(pk__in=body["ids"]).delete()

        return Response({"message": "Successfully deleted a user"})


class AuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        is_admin = user.is_superuser
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'isAdmin': is_admin})



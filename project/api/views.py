from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework import mixins

from django.contrib.auth import authenticate

from .jwt import JWTAuthentication
from .models import Hall, MaterialsPrices, MaterialsAmount, User
from .serializers import UserSerializer, HallSerializer, MaterialsPricesSerializer, MaterialsAmountSerializer, \
    ChangePasswordSerializer, LoginRegisterSerializer


class LoginView(GenericAPIView):
    """
    Login view - here user gets auth token.
    """
    serializer_class = LoginRegisterSerializer

    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        user = authenticate(username=email, password=password)

        if user:
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(GenericAPIView):
    """
    Register view - also provides first auth token, ready to use.
    """
    serializer_class = LoginRegisterSerializer

    @staticmethod
    def post(request):
        serializer = LoginRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=request.data['username'],
                email=request.data['email'],
                password=request.data['password'],
            )
            serializer = LoginRegisterSerializer(user, many=False)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    """
    User views with various permissions and querysets - depends on method.
    """
    queryset = User.objects.all().order_by('-date_joined')
    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):
        if self.action in ['update']:
            serializer_class = ChangePasswordSerializer
        else:
            serializer_class = UserSerializer
        return serializer_class

    def get_permissions(self):
        if self.action in ['retrieve', 'update']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            users = User.objects.all()
            return users
        user_to_return = User.objects.filter(id=user.id)
        return user_to_return

    def update(self, request, **kwargs):
        old_password = request.data.get('old_password', None)
        new_password = request.data.get('new_password', None)
        user = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(old_password):
                return Response("Wrong password.", status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            return Response("Password changed successfully.", status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HallSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page'
    max_page_size = 100


class HallViewSet(viewsets.ModelViewSet):
    """
    Halls views.
    create() method calculates base value of the steel hall.
    """
    queryset = Hall.objects.all()
    serializer_class = HallSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['project_id', '@salesman', 'calculated_value', 'roof_slope']
    ordering = ['-project_id']
    pagination_class = HallSetPagination

    def get_queryset(self):
        return Hall.objects.filter(salesman=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = HallSerializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = HallSerializer(data=request.data)
        if serializer.is_valid():
            hall = Hall.objects.create(
                salesman=self.request.user,
                length=request.data['length'],
                width=request.data['width'],
                pole_height=request.data['pole_height'],
                roof_slope=request.data['roof_slope'],
            )
            serializer = HallSerializer(hall, many=False)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        serializer = HallSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            hall = self.get_object()
            hall.length = request.data['length']
            hall.width = request.data['width']
            hall.pole_height = request.data['pole_height']
            hall.roof_slope = request.data['roof_slope']
            hall.save()
            serializer = HallSerializer(hall, many=False)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        hall = self.get_object()
        hall.delete()
        return Response(data='Project deleted.')

    @action(detail=True, methods=['GET'])
    def calculate(self):
        """
        Business logic here.
        """
        hall = self.get_object()
        materials = MaterialsAmount.objects.filter(project=hall.project_id)
        value = float(hall.length) * float(hall.width) * 833.33
        for material in materials:
            value += float(material.amount) * float(material.material.price)
        hall.calculated_value = value
        hall.save()
        serializer = HallSerializer(hall, many=False)
        return Response(serializer.data)


class MaterialsPricesViewSet(viewsets.ModelViewSet):
    """
    Basic views of materials with prices.
    """
    queryset = MaterialsPrices.objects.all()
    serializer_class = MaterialsPricesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_fields = ['material', 'price']


class MaterialsAmountViewSet(viewsets.ModelViewSet):
    """
    Basic views of material amount for particular project.
    User can search materials for project by query param.
    """
    queryset = MaterialsAmount.objects.all()
    serializer_class = MaterialsAmountSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_fields = ['project', 'material']

    def get_queryset(self):
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            halls = MaterialsAmount.objects.filter(project=project_id)
            return halls
        halls = MaterialsAmount.objects.all()
        return halls

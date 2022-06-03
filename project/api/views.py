from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action

from django.contrib.auth.models import User

from .models import Hall, MaterialsPrices, MaterialsAmount
from .serializers import UserSerializer, HallSerializer, MaterialsPricesSerializer, MaterialsAmountSerializer, \
    ChangePasswordSerializer


class HallSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """
    User views with various permissions and querysets - depends on REST method.
    """
    queryset = User.objects.all().order_by('-date_joined')
    authentication_classes = [TokenAuthentication]

    def get_serializer_class(self):
        if self.action in ['update']:
            serializer_class = ChangePasswordSerializer
        else:
            serializer_class = UserSerializer
        return serializer_class

    def get_permissions(self):
        if self.action in ['retrieve', 'update']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['create']:
            permission_classes = [AllowAny]
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


class HallViewSet(viewsets.ModelViewSet):
    """
    Halls views.
    create() method calculates base value of the steel hall.
    """
    queryset = Hall.objects.all()
    serializer_class = HallSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filter_fields = ['project_id', 'salesman', 'calculated_value']
    search_fields = ['project_id', '@salesman']
    ordering = ['-project_id']
    pagination_class = HallSetPagination

    def get_queryset(self):
        user = self.request.user.id
        if user:
            halls = Hall.objects.filter(salesman=user)
            return halls
        halls = Hall.objects.all()
        return halls

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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class MaterialsAmountViewSet(viewsets.ModelViewSet):
    """
    Basic views of material amount for particular project.
    User can search materials for project by query param.
    """
    queryset = MaterialsAmount.objects.all()
    serializer_class = MaterialsAmountSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            halls = MaterialsAmount.objects.filter(project=project_id)
            return halls
        halls = MaterialsAmount.objects.all()
        return halls
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Hall, MaterialsPrices, MaterialsAmount


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
        ]
        extra_kwargs = {'password': {'required': True, 'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for User update endpoint.
    """
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class HallSerializer(serializers.ModelSerializer):
    salesman = serializers.StringRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Hall
        fields = [
            'project_id',
            'salesman',
            'length',
            'width',
            'pole_height',
            'roof_slope',
            'update_date',
            'calculated_value',
        ]
        read_only_fields = ['project_id']


class MaterialsPricesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialsPrices
        fields = [
            'material_id',
            'material',
            'price',
            'update_date',
        ]


class MaterialsAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialsAmount
        fields = [
            'amount_id',
            'project',
            'material',
            'amount',
            'update_date',
        ]

    def update(self, instance, validated_data):
        instance.material = validated_data.get('material', instance.material)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance

from rest_framework import serializers
from my_app.models import CustomUser, Category, Shop, ProductInfo, Product, ProductParameter, OrderItem, Order, Contact
from rest_framework.validators import UniqueValidator
from django.contrib.auth import password_validation
from django.contrib.auth.validators import UnicodeUsernameValidator


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all()),
        ],
    )
    first_name = serializers.CharField(validators=[UnicodeUsernameValidator()])
    last_name = serializers.CharField(validators=[UnicodeUsernameValidator()])

    class Meta:
        """UserSerializer Meta."""

        model = CustomUser
        fields = (
            'id',
            'VariationUser',
            'first_name',
            'last_name',
            'email',
            'company',
            'position',
            'contacts',
            'shop_id'
        )
        read_only_fields = ('id',)


class UserCreateSerializer(UserSerializer):
    password = serializers.CharField(
        validators=[password_validation.validate_password]
    )

    class Meta:
        """UserSerializer Meta."""

        model = CustomUser
        fields = (
            'id',
            'first_name',
            'last_name',
            'password',
            'email',
            'company',
            'position',
            # 'contacts',
        )
        read_only_fields = ('id',)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        validators=[password_validation.validate_password]
    )

    class Meta:
        """UserSerializer Meta."""

        model = CustomUser
        fields = ('id', 'password', 'email')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ShopSerializer(serializers.ModelSerializer):
    state = serializers.BooleanField()

    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Shop
        fields = ('id', 'name', 'url', 'state', 'user')
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        """ProductSerializer Meta."""
        model = Product
        fields = ('name', 'category',)


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        """ProductParameterSerializer Meta."""
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        """ProductInfoSerializer Meta."""
        model = ProductInfo
        fields = ('id', 'model', 'product', 'shop', 'quantity', 'price', 'price_rrc', 'product_parameters',)
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    product_info = serializers.PrimaryKeyRelatedField(queryset=ProductInfo.objects.all())
    quantity = serializers.IntegerField(min_value=1, max_value=1000, default=1)

    class Meta:
        """OrderItemSerializer Meta."""
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }


class OrderItemUpdSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=OrderItem.objects.all())
    quantity = serializers.IntegerField(min_value=1, max_value=1000, default=1)

    class Meta:
        """OrderItemSerializer Meta."""

        model = OrderItem
        fields = (
            'id',
            'product_info',
            'quantity',
            'order',
        )
        read_only_fields = ('id',)
        extra_kwargs = {'order': {'write_only': True}}


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)
    state = serializers.CharField(required=False, read_only=True)
    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        """OrderSerializer Meta."""
        model = Order
        fields = ('id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact',)
        read_only_fields = ('id',)


class OrderUpdSerializer(OrderSerializer):
    contact = serializers.IntegerField()


class OrderDelSerializer(serializers.ModelSerializer):
    ordered_items = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=1000)
    )

    class Meta:
        """OrderSerializer Meta."""

        model = Order
        fields = (
            'id',
            'ordered_items'
        )
        read_only_fields = ('id', 'ordered_items')
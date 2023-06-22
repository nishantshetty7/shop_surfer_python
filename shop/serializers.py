from rest_framework.serializers import ModelSerializer
from shop.models import Category, Product, Cart, CartItem


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class CartItemSerializer(ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity', 'is_selected']
        # read_only_fields = ['id']

    # def create(self, validated_data):
    #     product_data = validated_data.pop('product')
    #     product = Product.objects.create(**product_data)
    #     cart_item = CartItem.objects.create(product=product, **validated_data)
    #     return cart_item

    # def update(self, instance, validated_data):
    #     product_data = validated_data.pop('product', None)
    #     if product_data:
    #         product = instance.product
    #         for attr, value in product_data.items():
    #             setattr(product, attr, value)
    #         product.save()
    #     instance.quantity = validated_data.get('quantity', instance.quantity)
    #     instance.save()
    #     return instance
    
    # def partial_update(self, instance, validated_data):
    #     return self.update(instance, validated_data)
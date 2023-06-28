from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import CategorySerializer, ProductSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, ShippingAddressSerializer
from shop.models import Product, Category, Cart, CartItem, Order, OrderItem, ShippingAddress
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from base.utils import get_object_or_none
    
@api_view(['GET'])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_products(request, pk):
    category_id = pk
    products = Product.objects.filter(category_id=category_id)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def product_detail(request, pk):
    product = get_object_or_none(Product, pk=pk)
    if product:
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
    return Response(
            {"error": "Product not found."},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart_list(request):

    user = request.user
    cart_list = []
    cart = get_object_or_none(Cart, user=user)
    if cart:
        latest_cart = CartItem.objects.filter(cart__user=user).order_by("created_at")
        serializer = CartItemSerializer(latest_cart, many=True)
        cart_list = serializer.data
    
    return Response(cart_list, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_cart_item(request):

    user = request.user
    cart_item_dict = dict(request.data)
    cart = get_object_or_none(Cart, user=user)
    if not cart:
        cart = Cart.objects.create(user=user)
    
    cart_item_dict["cart_id"] = cart.id
    print(cart_item_dict)

    # Check if the product exists
    product = get_object_or_none(Product, id=cart_item_dict.get("product_id"))

    try:
        if cart and product:
            CartItem.objects.create(**cart_item_dict)

            latest_cart = CartItem.objects.filter(cart__user=user).order_by("created_at")
            serializer = CartItemSerializer(latest_cart, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
    except IntegrityError:
        pass
    
    return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

        

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def merge_cart(request):

    user = request.user
    cart_items = request.data
    cart = get_object_or_none(Cart, user=user)
    if not cart:
        cart = Cart.objects.create(user=user)

    item_objects = []
    for item in cart_items:
        if item.get("product", None):
            item_obj = CartItem(cart=cart, product_id=item["product"]["id"],
                                quantity=item["quantity"], is_selected=item["is_selected"])
            # print(item_obj.product_id)
            item_objects.append(item_obj)

    if len(item_objects) > 0:

        item_objects_old = CartItem.objects.filter(cart__user=user).order_by("created_at")
        if len(item_objects_old) > 0:
            # Check for duplicates
            existing_ids = set(item_objects_old.values_list('product_id', flat=True))
            duplicate_items = [obj for obj in item_objects if obj.product_id in existing_ids]
            
            # Filter out duplicates from the original list
            unique_cart_items = [obj for obj in item_objects if obj not in duplicate_items]

            for obj in duplicate_items:
                CartItem.objects.filter(product_id=obj.product_id).update(quantity=obj.quantity,
                                                        is_selected=obj.is_selected)
        else:
            unique_cart_items = item_objects

        valid_products = Product.objects.filter(id__in=[obj.product_id for obj in unique_cart_items]).values_list("id", flat=True)
        print(valid_products)

        valid_cart_items = [obj for obj in unique_cart_items if obj.product_id in valid_products]
        try:
            CartItem.objects.bulk_create(valid_cart_items, ignore_conflicts=True)
        except IntegrityError:
            pass


        latest_cart = CartItem.objects.filter(cart__user=user).order_by("created_at")
        serializer = CartItemSerializer(latest_cart, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_cart_item(request):
    print(request.data)
    # item_id = request.data.pop("item_id", None)
    product_id = request.data.pop("product_id", None)
    user = request.user
    updated = True
    if product_id and ("quantity" in request.data or "is_selected" in request.data):
        latest_cart = CartItem.objects.filter(cart__user=user).order_by("created_at")
        latest_cart.filter(product_id=product_id).update(**request.data)
    elif not product_id and "is_selected" in request.data:
        latest_cart = CartItem.objects.filter(cart__user=user).order_by("created_at")
        latest_cart.update(is_selected=request.data["is_selected"])
    else:
        updated = False

    if updated:
        serializer = CartItemSerializer(latest_cart, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])           
def delete_cart_item(request):
    # item_id = request.data.pop("item_id", None)
    product_ids = request.data.pop("product_ids", None)
    user = request.user

    if product_ids:
        latest_cart = CartItem.objects.filter(cart__user=user).order_by("created_at")
        latest_cart.filter(product_id__in=product_ids).delete()
        serializer = CartItemSerializer(latest_cart, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
            

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):

    user = request.user
    order_data = request.data.pop("order", None)
    order_items = request.data.pop("order_items", None)

    if order_data and order_items:
        order_data["user_id"] = user.id
        order_obj = Order(**order_data)

        item_objects = []
        for item in order_items:
            if item.get("product_id", None):
                item_obj = OrderItem(order=order_obj, product_id=item["product_id"],
                                    price=item["price"], quantity=item["quantity"])
                item_objects.append(item_obj)

        if len(item_objects) > 0:
            
            valid_products = Product.objects.filter(id__in=[obj.product_id for obj in item_objects]).values_list("id", flat=True)
            print(valid_products)

            valid_order_items = [obj for obj in item_objects if obj.product_id in valid_products]
            if len(valid_order_items) > 0:
                order_obj.save()
                try:
                    OrderItem.objects.bulk_create(valid_order_items, ignore_conflicts=True)
                except IntegrityError:
                    pass

                order_serializer = OrderSerializer(order_obj)
                response_data = order_serializer.data
                item_objects = OrderItem.objects.filter(order=order_obj)
                item_serializer = OrderItemSerializer(item_objects, many=True)
                
                response_data["order_items"] = item_serializer.data

                return Response(response_data, status=status.HTTP_200_OK)
        
    return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_address_list(request):

    user = request.user
    address_list = ShippingAddress.objects.filter(user=user).order_by("created_at")
    serializer = ShippingAddressSerializer(address_list, many=True)
    updated_list = []
    for addr in serializer.data:
        addr["is_selected"] = True if addr["is_default"] else False

        updated_list.append(addr)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_address(request):

    user = request.user
    new_address = dict(request.data)

    if new_address:
        new_address["user_id"] = user.id
        address_list = ShippingAddress.objects.filter(user=user).order_by("created_at")
        if len(address_list) == 0:
            new_address["is_default"] = True
        
        new_address_obj = ShippingAddress.objects.create(**new_address)

        latest_list = ShippingAddress.objects.filter(user=user).order_by("created_at")
        serializer = ShippingAddressSerializer(latest_list, many=True)
        updated_list = []
        for addr in serializer.data:
            addr["is_selected"] = True if addr["id"] == new_address_obj.id else False

            updated_list.append(addr)

        return Response(updated_list, status=status.HTTP_200_OK)
    
    return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_address(request):

    user = request.user
    updated_address = dict(request.data)
    address_id = updated_address.pop("id", None)
    updated_address.pop("is_selected")
    updated = False

    if address_id:
        address_obj = ShippingAddress.objects.filter(id = address_id)
        if len(address_obj) > 0:
            address_obj.update(**updated_address)
            updated = True

        latest_list = ShippingAddress.objects.filter(user=user).order_by("created_at")
        serializer = ShippingAddressSerializer(latest_list, many=True)
        updated_list = []
        for addr in serializer.data:
            if updated:
                addr["is_selected"] = True if addr["id"] == address_id else False
            else:
                addr["is_selected"] = True if addr["is_default"] else False

            updated_list.append(addr)

        return Response(updated_list, status=status.HTTP_200_OK)
    
    return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

# class CartItemRetrieveUpdateDelete(RetrieveUpdateDestroyAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = CartItemSerializer

#     def get_queryset(self):
#         cart_item_id = self.kwargs['pk']
#         user = self.request.user
#         return CartItem.objects.filter(cart__user=user, id=cart_item_id)
    
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def perform_destroy(self, instance):
#         instance.delete()
#         return Response({'message': 'Cart item deleted.'}, status=status.HTTP_204_NO_CONTENT)
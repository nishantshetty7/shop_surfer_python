from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import CategorySerializer, ProductSerializer, CartSerializer, CartItemSerializer
from shop.models import Product, Category, Cart, CartItem
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

        

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_cart_item(request):
    print(request.data)
    item_id = request.data.pop("item_id", None)
    user = request.user
    updated = True
    if item_id and ("quantity" in request.data or "is_selected" in request.data):
        CartItem.objects.filter(id=item_id).update(**request.data)
    elif not item_id and "is_selected" in request.data:
        CartItem.objects.filter(cart__user=user).update(is_selected=request.data["is_selected"])
    else:
        updated = False

    if updated:
        latest_cart = CartItem.objects.filter(cart__user=user).order_by("created_at")
        serializer = CartItemSerializer(latest_cart, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])           
def delete_cart_item(request):
    item_id = request.data.pop("item_id", None)
    product_id = request.data.pop("product_id", None)
    user = request.user
    updated = True
    if item_id:
        CartItem.objects.filter(id=item_id).delete()
    elif product_id:
        CartItem.objects.filter(cart__user=user, product_id=product_id).delete()  
    else:
        updated = False

    if updated:
        latest_cart = CartItem.objects.filter(cart__user=user).order_by("created_at")
        serializer = CartItemSerializer(latest_cart, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
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
from rest_framework import serializers
from .models import *


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'sku', 'description']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['file_path']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['variant_title', 'variant', 'product']

class ProductVariantPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantPrice
        fields = ['product_variant_one', 'product_variant_two', 'product_variant_three', 'price', 'stock']

class CreateProductSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    sku = serializers.SlugField(max_length=255)
    description = serializers.CharField()
    product_image = ProductImageSerializer(many=True, required=False)
    product_variant = serializers.ListSerializer(child=serializers.DictField(), required=False)
    product_variant_prices = serializers.ListSerializer(child=serializers.DictField(), required=False)

    def create(self, validated_data):
        # Create the product object
        product = Product.objects.create(**validated_data)

        # Create product images if available
        product_images_data = validated_data.pop('product_image', [])
        for product_image_data in product_images_data:
            ProductImage.objects.create(product=product, **product_image_data)

        # Create product variants and prices if available
        product_variants_data = validated_data.pop('product_variant', [])
        product_variant_prices_data = validated_data.pop('product_variant_prices', [])
        for variant_data in product_variants_data:
            variant_title = variant_data.pop('title')
            variant = Variant.objects.get_or_create(title=variant_title, defaults=variant_data)[0]
            ProductVariant.objects.create(product=product, variant=variant, **variant_data)

        for price_data in product_variant_prices_data:
            product_variant_one_title = price_data.pop('title')
            product_variant_one = ProductVariant.objects.get(variant_title=product_variant_one_title)
            ProductVariantPrice.objects.create(product=product, product_variant_one=product_variant_one, **price_data)

        return product

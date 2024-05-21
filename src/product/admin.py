from django.contrib import admin
from .models import Variant, Product, ProductImage, ProductVariant, ProductVariantPrice

class VariantAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'active', 'created_at', 'updated_at')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'sku', 'description', 'created_at', 'updated_at')

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'file_path', 'created_at', 'updated_at')

class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('variant_title', 'variant', 'product', 'created_at', 'updated_at')

class ProductVariantPriceAdmin(admin.ModelAdmin):
    list_display = ('get_product_title', 'get_variant_titles', 'price', 'stock', 'created_at', 'updated_at')

    def get_product_title(self, obj):
        return obj.product.title if obj.product else None

    get_product_title.short_description = 'Product'

    def get_variant_titles(self, obj):
        variants = []
        if obj.product_variant_one:
            variants.append(obj.product_variant_one.variant_title)
        if obj.product_variant_two:
            variants.append(obj.product_variant_two.variant_title)
        if obj.product_variant_three:
            variants.append(obj.product_variant_three.variant_title)
        return ', '.join(variants) if variants else None

    get_variant_titles.short_description = 'Variants'

admin.site.register(Variant, VariantAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(ProductVariantPrice, ProductVariantPriceAdmin)

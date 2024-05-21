from django.views import generic
from django.views.generic import ListView, UpdateView
from django.shortcuts import render
from django.urls import reverse_lazy
from product.models import Product, ProductVariant, ProductVariantPrice, Variant
from datetime import datetime
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.utils.dateparse import parse_date

class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context



class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_queryset(self):
        queryset = Product.objects.order_by('-created_at').distinct()
        title = self.request.GET.get('title')
        variant_title = self.request.GET.get('variant_title')
        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')
        date = self.request.GET.get('date')

        if title:
            queryset = queryset.filter(title__icontains=title)

        if variant_title:
            queryset = queryset.filter(
                productvariant__variant_title=variant_title
            )

        if price_from:
            queryset = queryset.filter(productvariantprice__price__gte=price_from)

        if price_to:
            queryset = queryset.filter(productvariantprice__price__lte=price_to)

        if date:
            queryset = queryset.filter(created_at=date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()  # Get the queryset

        # Paginate the queryset
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        try:
            products = paginator.page(page_number)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        context['products'] = products

        # Prepare variants grouped by type
        variants = ProductVariant.objects.values('variant__title', 'variant_title').distinct()
        grouped_variants = {}
        for variant in variants:
            variant_type = variant['variant__title']
            variant_title = variant['variant_title']
            if variant_type not in grouped_variants:
                grouped_variants[variant_type] = []
            grouped_variants[variant_type].append(variant_title)
        context['grouped_variants'] = grouped_variants

        context['title'] = self.request.GET.get('title', '')
        context['variant_title'] = self.request.GET.get('variant_title', '')
        context['price_from'] = self.request.GET.get('price_from', '')
        context['price_to'] = self.request.GET.get('price_to', '')
        context['date'] = self.request.GET.get('date', '')

        # Calculate start and end index for current page
        context['start_index'] = (products.number - 1) * self.paginate_by + 1
        context['end_index'] = min(products.number * self.paginate_by, products.paginator.count)

        return context



class ProductUpdateView(UpdateView):
    model = Product
    template_name = 'products/update.html'
    fields = ['title', 'description', 'sku']

    def get_success_url(self):
        return reverse_lazy('product:list.product')
    


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from product.models import Product
from product.serializers import ProductSerializer, ProductVariantSerializer, ProductVariantPriceSerializer, ProductImageSerializer



class ProductCreateApiView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        title = data.get('title')
        
        try:
            product = Product.objects.get(title=title)
        except Product.DoesNotExist:
            product_data = {
                'title': title,
                'sku': data.get('sku'),
                'description': data.get('description')
            }
            product_serializer = ProductSerializer(data=product_data)
            if product_serializer.is_valid():
                product = product_serializer.save()
            else:
                return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create product variants
        variants_data = data.get('product_variant', [])
        for variant_data in variants_data:
            for tag in variant_data['tags']:
                variant_query = ProductVariant.objects.filter(variant_title=tag, product=product)
                if variant_query.exists():
                    variant = variant_query.first()
                else:
                    variant = ProductVariant.objects.create(
                        variant_title=tag,
                        variant_id=variant_data['option'],
                        product=product
                    )
                # Save the variant
                variant.save()

        # Create product variant prices for each variant
        prices_data = data.get('product_variant_prices', [])
        for price_data in prices_data:
            product_variant_title = price_data['title'][:-1]  # Remove the last character "/" from the title
            variant_titles = product_variant_title.split('/')  # Split the title into separate variant titles

            # Get the ProductVariant objects for each separate variant
            variants = []
            for variant_title in variant_titles:
                variant_query = ProductVariant.objects.filter(variant_title=variant_title, product=product)
                if variant_query.exists():
                    variants.append(variant_query.first())
                else:
                    # If the variant does not exist, continue to the next price_data
                    continue

            # Create the ProductVariantPrice object
            product_variant_price = ProductVariantPrice.objects.create(
                price=price_data['price'],
                stock=price_data['stock'],
                product=product
            )

            # Assign the product variants to the ProductVariantPrice object
            if variants:
                product_variant_price.product_variant_one = variants[0]
            if len(variants) > 1:
                product_variant_price.product_variant_two = variants[1]
            if len(variants) > 2:
                product_variant_price.product_variant_three = variants[2]
            product_variant_price.save()

        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)





from django.middleware.csrf import get_token
from django.http import JsonResponse

def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})


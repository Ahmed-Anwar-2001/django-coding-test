from django.urls import path
from django.views.generic import TemplateView

from product.views.product import CreateProductView, ProductListView, ProductUpdateView, ProductCreateApiView, get_csrf_token
from product.views.variant import VariantView, VariantCreateView, VariantEditView, VariantDeleteView

app_name = "product"

urlpatterns = [
    # Variants URLs
    path('variants/', VariantView.as_view(), name='variants'),
    path('variant/create', VariantCreateView.as_view(), name='create.variant'),
    path('variant/<int:id>/edit', VariantEditView.as_view(), name='update.variant'),
    path('variant/<int:pk>/delete/', VariantDeleteView.as_view(), name='delete.variant'),

    # Products URLs
    path('create/', CreateProductView.as_view(), name='create.product'),
    path('list/', ProductListView.as_view(), name='list.product'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='update.product'), 
    path('api/create/', ProductCreateApiView.as_view(), name='api.create.product'),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
]

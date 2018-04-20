"""MapPro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from MapPro.accounts.views import UserViewSet, AuthToken, UserDelete
from MapPro.orders.views import ColorMarkerViewSet, OrderViewSet, ArchiveOrderViewSet, \
    OrderWithAddressCount, OrdersByUsersAndDateRange, ColorMarkerDelete, OrderDelete, OrderDeleteByDateRange,\
    OrderMassFilter, NoDateOrdersViewSet, GenerateInvoiceViewSet, MyOrders, UserOrdersViewSet, \
    UserOrderByDateViewSet, MyTodayOrders, TableViewSet, DeArchiveOrderViewSet, GoogleMapsAutocompleteCaller

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('users', UserViewSet)
router.register('colors/delete-marker', ColorMarkerDelete, base_name='colors/delete-marker')
router.register('colors', ColorMarkerViewSet)
router.register('delete/by-date', OrderDeleteByDateRange, base_name='delete/by-date')
router.register('orders/delete', OrderDelete, base_name='orders/delete')
router.register('mass-filter', OrderMassFilter, base_name='mass-filter')
router.register('no-date', NoDateOrdersViewSet, base_name='no-date')
router.register('invoice', GenerateInvoiceViewSet, base_name='invoice')
router.register('my-orders', MyOrders, base_name='my-orders')
router.register('orders', OrderViewSet)
router.register('archive', ArchiveOrderViewSet, base_name='archive')
router.register('dearchive', DeArchiveOrderViewSet, base_name='dearchive')
router.register('count', OrderWithAddressCount, base_name='count')
router.register('filter', OrdersByUsersAndDateRange, base_name='filter')
router.register('user-orders', UserOrdersViewSet, base_name='user-orders')
router.register('delete-user', UserDelete, base_name='delete-user')
router.register('today', MyTodayOrders, base_name='today')
router.register('my-orders-by-date', UserOrderByDateViewSet, base_name='my-orders-by-date')
router.register('table', TableViewSet, base_name='table')
router.register('google-maps-autocomplete', GoogleMapsAutocompleteCaller, base_name='google-maps-autocomplete')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', AuthToken.as_view()),
]

from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY
from .models import ColorMarker, Order, User
from .serielizers import ColorMarkerSerializer, OrderSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .permissions import IsNotAdmin
import json
import os
import datetime
import time
import pandas as pd
import requests
import base64
import openpyxl
from django.core.paginator import Paginator


class ColorMarkerViewSet(ModelViewSet):

    queryset = ColorMarker.objects.all()
    serializer_class = ColorMarkerSerializer
    permission_classes = (IsAuthenticated,)


class OrderViewSet(ModelViewSet):

    queryset = Order.objects.filter(is_archived=False).all().order_by('-id')
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'patch', 'put']

    def create(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        user = User.objects.get(pk=data['user'])
        order_count = Order.objects.filter(user=user, date__isnull=False, date=data['date'], time_from__isnull=False,
                                           time_from=data['timeFrom']).count()
        if order_count > 0:
            return Response({"message": "An order for user" + user.get_full_name() + " already exists at specified date and time"}, status=HTTP_422_UNPROCESSABLE_ENTITY)
        return super(OrderViewSet, self).create(request, args, kwargs)


class ArchiveOrderViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request, format=None):
        str = request.body.decode('utf-8')[1:-1].split(',')
        Order.objects.filter(pk__in=str).update(is_archived=True)
        return Response({'message': 'success'})


class DeArchiveOrderViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request, format=None):
        str = request.body.decode('utf-8')[1:-1].split(',')
        Order.objects.filter(pk__in=str).update(is_archived=False)
        return Response({'message': 'success'})


class ColorMarkerDelete(ViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    def create(self, request):
        body = json.loads(request.body.decode('utf-8'))
        if not request.user.check_password(body["password"]):
            return Response(status=HTTP_422_UNPROCESSABLE_ENTITY, data={"message": 'Password not correct'})
        to_delete_color = ColorMarker.objects.get(pk=body["id"])
        related_orders = Order.objects.filter(color_marker=to_delete_color)
        default_color = ColorMarker.objects.filter(default=True).first()
        if to_delete_color == default_color:
            return Response(status=HTTP_422_UNPROCESSABLE_ENTITY, data={"message": "You cannot delete the default color"})
        related_orders.update(color_marker=default_color)
        to_delete_color.delete()

        return Response({"message": "Successfully deleted a color marker"})


class OrderWithAddressCount(ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request, format=None):
        count = Order.objects.filter(address=request.body.decode('utf-8')).count()
        return Response({'count': count})


class OrdersByUsersAndDateRange(ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request, format=None):
        search = json.loads(request.body.decode('utf-8'))
        print(search, search["users"], search["colors"], len(search["colors"]))
        print(search["users"]) or len(search["colors"])
        if len(search["users"]) == 0 and len(search["colors"]) == 0:
            print('mtaaaav ara mtaaaaaav')
            return Response([])
        if len(search["users"]) and len(search["colors"]):
            print('mtav 1')
            orders = Order.objects.filter(
                time_from__isnull=False,
                address__icontains=search.get("searchString", ""),
                user__in=search["users"],
                color_marker__in=search["colors"],
                date__isnull=False,
                date__gte=search["range"][0],
                date__lte=search["range"][1]
            ).all()
        elif len(search["users"]):
            print('mtav 2')
            orders = Order.objects.filter(
                time_from__isnull=False,
                address__icontains=search.get("searchString", ""),
                user__in=search["users"],
                date__isnull=False,
                date__gte=search["range"][0],
                date__lte=search["range"][1]
            ).all()
        elif len(search["colors"]):
            print('mtav 3')
            orders = Order.objects.filter(
                time_from__isnull=False,
                color_marker__in=search["colors"],
                address__icontains=search.get("searchString", ""),
                date__isnull=False,
                date__gte=search["range"][0],
                date__lte=search["range"][1]
            ).all()
        else:
            print('mtav 4')
            orders = Order.objects.filter(
                time_from__isnull=False,
                date__isnull=False,
                address__icontains=search.get("searchString", ""),
                date__gte=search["range"][0],
                date__lte=search["range"][1]
            ).all()

        print(orders.count(), 'cnt')
        orders = OrderSerializer(orders, many=True)
        return Response(orders.data)


class OrderMassFilter(ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        body = json.loads(request.body.decode('utf-8'))
        search = body.get("search", "")
        colors = body.get("colors", [])
        date = body.get("date", "")
        if not (search or date or len(colors)):
            print("Entered because no something", search, date, colors)
            return Response([])

        queryset = Order.objects.filter(
            Q(address__icontains=search) | Q(name__icontains=search)
        )
        if date:
            queryset = queryset.filter(date=date)
        if len(colors):
            queryset = queryset.filter(color_marker__in=colors)
            print("REACHED END HAMARYA")
        orders = OrderSerializer(queryset, many=True)
        return Response(orders.data)


class OrderDeleteByDateRange(ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        body = json.loads(request.body.decode('utf-8'))
        date_from = body.get('from', None)
        queryset = Order.objects.filter(date__isnull=False)
        date_to = body.get('to', None)
        if not (date_from and date_to):
            return Response({"message": "Please provide a date"})
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)

        print(queryset.count(), date_from, date_to, 'count')
        queryset.delete()

        return Response({"message": "Successfully deleted"})


class OrderDelete(ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        body = json.loads(request.body.decode('utf-8'))
        if not request.user.check_password(body["password"]):
            return Response(status=HTTP_422_UNPROCESSABLE_ENTITY, data={"message": 'Password not correct'})
        Order.objects.filter(pk__in=body["ids"]).delete()

        return Response({"message": "Successfully deleted an order"})


class NoDateOrdersViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ('post',)

    def create(self, request):
        orders = Order.objects.filter(date__isnull=True).order_by('-pk')
        orders = OrderSerializer(orders, many=True)
        return Response(orders.data)


class GenerateInvoiceViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ('post',)

    def create(self, request):
        body = json.loads(request.body.decode('utf-8'))
        pk = body.get("pk")
        order = Order.objects.get(pk=pk)
        path = os.path.dirname(os.path.abspath(__file__))
        # open_file = pd.read_excel()
        srcfile = openpyxl.load_workbook(path + '/INVOICE.xlsx')  # to open the excel sheet and if it has macros

        sheetname = srcfile.get_sheet_by_name('GUARDIAN')  # get sheetname from the file
        sheetname['H10'] = str(order.name + '\n' + order.address + '\n' + 'Phone: ' + order.mobile_phone)  # write something in B2 cell of the supplied sheet
        # sheetname.cell(row=1,
        #                column=1).value = "something"  # write to row 1,col 1 explicitly, this type of writing is useful to write something in loops

        srcfile.save(path + '/INVOICE2.xlsx')
        file = open(path + '/INVOICE2.xlsx', 'r+', encoding="utf8", errors='ignore')
        file_content = file.read()

        base64_two = base64.b64encode(bytes(file_content, encoding='utf-8')).decode('ascii')
        # open_sheet = open_file.get_sheet_by_name('GUARDIAN')
        # # open_sheet['J5'] = str(datetime.date.today())
        # open_file.save()

        return Response({"file": repr(base64_two)})


class MyOrders(ViewSet):
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get', 'post',)

    def create(self, request):
        body = json.loads(request.body.decode('utf-8'))
        order = Order.objects.get(pk=body['order'])
        color = ColorMarker.objects.get(pk=body['color'])
        order.color_marker = color
        order.save()
        return Response({"message": "success"})

    def list(self, request):
        orders = Order.objects.filter(user=request.user, date__isnull=False).order_by('-date')
        orders = OrderSerializer(orders, many=True)

        return Response(orders.data)


class MyTodayOrders(ViewSet):
    permission_classes = (IsAuthenticated, IsNotAdmin,)
    http_method_names = ('get', 'post',)

    def list(self, request):
        orders = Order.objects.filter(user=request.user, date=datetime.date.today()).order_by('-pk')
        orders = OrderSerializer(orders, many=True)

        return Response(orders.data)


class UserOrdersViewSet(ViewSet):
    http_method_names = ('get',)
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk):
        user = User.objects.get(pk=pk)
        orders = Order.objects.filter(user=user, date__isnull=False).order_by('-date')
        orders = OrderSerializer(orders, many=True)

        return Response(orders.data)


class UserOrderByDateViewSet(ViewSet):
    http_method_names = ('post',)
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        body = json.loads(request.body.decode('utf-8'))
        date = body.get('date')
        orders = Order.objects.filter(date=date, user=request.user)
        orders = OrderSerializer(orders, many=True)

        return Response(orders.data)


class TableViewSet(ViewSet):
    http_method_names = ('post',)
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        body = json.loads(request.body.decode('utf-8'))
        address =body.get('address', None)
        mobile = body.get('mobilePhone', None)
        color = body.get('color', None)
        name = body.get('name', None)
        user = body.get('user', None)
        rank = body.get('rank', None)
        if rank:
            rank = rank.encode('utf-8')
            rank = int(rank)
            orders = Order.objects.all()
            for order in list(orders):
                print(order.get_rank, rank, order.get_rank == rank, 'hello')
                if order.get_rank == rank:
                    orders_final = OrderSerializer(Order.objects.filter(pk=order.id), many=True)
                    return Response({"count": Order.objects.count(), "data": orders_final.data})
            return Response({"count": 0, "data": []})
        orders = Order.objects.order_by('-pk')
        if name:
            orders = orders.filter(name__icontains=name)
        if address:
            orders = orders.filter(address__icontains=address)
        if mobile:
            orders = orders.filter(mobile_phone__icontains=mobile)
        if color:
            orders = orders.filter(color_marker__in=color)
        if user:
            orders = orders.filter(user__in=user)
        count = Order.objects.count()
        paginator = Paginator(orders.all(), 20)
        page = body.get('page', 1)
        orders = paginator.page(page)
        orders = orders.object_list
        orders = OrderSerializer(orders.all(), many=True)
        return Response({"count": count, "data": orders.data})


class GoogleMapsAutocompleteCaller(ViewSet):
    http_method_names = ('get',)
    permission_classes = (AllowAny,)
    maps_api_url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?' \
                   'key=AIzaSyD88Itl-8yLLJxhCG7EHQtSNA3TrK52Aik'

    def list(self, request):
        address = request.GET.get('address', None)
        r = requests.get(self.maps_api_url + '&input=' + address)
        return Response(r.json())

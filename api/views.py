from datetime import timedelta, datetime
from django.db.models.aggregates import Sum, Count
from django.conf import settings
import urllib
import json
from django.db.models import Q
import os
from dyn import get_data

from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import generics, mixins, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
import pymysql
from api import serializers
from api.serializers import UserSerializer
from main import models
from main.models import WellMatrix
from main.serializers import WellMatrixCreateSerializer, WellMatrixSerializer, WellSerializer, FieldSerializer, \
    FieldBalanceSerializer, FieldBalanceCreateSerializer, DepressionSerializer, TSSerializer, ProdProfileSerializer, \
    GSMSerializer, DynamogramSerializer, ImbalanceSerializer
from django.core.mail import EmailMessage


class AuthView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })


class ListUser(generics.ListCreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class DetailUser(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class WellMatrixViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('well',)
    queryset = models.WellMatrix.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        # if self.request.user.type == User.CLIENT:
        #     return models.Application.objects.filter(user=self.request.user)
        return models.WellMatrix.objects.all()

    def get_serializer_class(self):
        if self.action == 'create_wellmatrix':
            return WellMatrixCreateSerializer
        return WellMatrixSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_field(self, request, *args, **kwargs):
        field = models.Field.objects.get(name=request.GET.get("field"))
        result = models.WellMatrix.objects.filter(well__field=field)
        return Response(WellMatrixSerializer(result, many=True).data)

    @action(methods=['post'], detail=False)
    def create_wellmatrix(self, request, *args, **kwargs):
        serializer = WellMatrixCreateSerializer(data=request.data)
        if serializer.is_valid():
            well = models.Well.objects.get(name=request.data["well"])
            dt = datetime.now()
            wellmatrix = WellMatrix.objects.update_or_create(well=well, defaults={"fluid": request.data["fluid"],
                                                                                  "teh_rej_fluid": request.data["teh_rej_fluid"],
                                                                                  "teh_rej_oil": request.data["teh_rej_oil"],
                                                                                  "teh_rej_water": request.data["teh_rej_water"],
                                                                                  "gas": request.data["gas"],
                                                                                  "timestamp": dt})
            return Response(self.get_serializer(wellmatrix, many=False).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepressionViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('well',)
    queryset = models.Depression.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return None

    def get_serializer_class(self):
        # if self.action == 'create_wellmatrix':
        #     return WellMatrixCreateSerializer
        return DepressionSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_well(self, request, *args, **kwargs):
        well = models.Well.objects.get(name=request.GET.get("well"))
        result = models.Depression.objects.filter(well=well)
        return Response(DepressionSerializer(result, many=True).data)

    @action(methods=['post'], detail=False)
    def create_depression(self, request, *args, **kwargs):
        serializer = WellMatrixCreateSerializer(data=request.data)
        if serializer.is_valid():
            well = models.Well.objects.get(name=request.data["well"])
            dt = datetime.now()
            wellmatrix = WellMatrix.objects.update_or_create(well=well, defaults={"fluid": request.data["fluid"],
                                                                                  "teh_rej_fluid": request.data["teh_rej_fluid"],
                                                                                  "teh_rej_oil": request.data["teh_rej_oil"],
                                                                                  "teh_rej_water": request.data["teh_rej_water"],
                                                                                  "gas": request.data["gas"],
                                                                                  "timestamp": dt})
            return Response(self.get_serializer(wellmatrix, many=False).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FieldBalanceViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('field',)

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return None

    def get_serializer_class(self):
        if self.action == 'create_balance':
            return FieldBalanceCreateSerializer
        return FieldBalanceSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_field(self, request, *args, **kwargs):
        field = models.Field.objects.get(name=request.GET.get("field"))
        result = models.FieldBalance.objects.filter(field=field, timestamp__year__gte=2019,
                                                    timestamp__month__gte=request.GET.get("month"),
                                                    timestamp__year__lte=2019,
                                                    timestamp__month__lte=request.GET.get("month"))
        return Response(FieldBalanceSerializer(result, many=True).data)

    @action(methods=['get'], detail=False)
    def get_total(self, request, *args, **kwargs):
        result = models.FieldBalance.objects.filter(timestamp__year__gte=2019,
                                                    timestamp__month__gte=request.GET.get("month"),
                                                    timestamp__year__lte=2019,
                                                    timestamp__month__lte=request.GET.get("month")).values('timestamp')\
            .annotate(transport_balance=Sum('transport_balance'), ansagan_balance=Sum('ansagan_balance'),
                      transport_brutto=Sum('transport_brutto'), ansagan_brutto=Sum('ansagan_brutto'),
                      transport_netto=Sum('transport_netto'), ansagan_netto=Sum('ansagan_netto'),
                      transport_density=Sum('transport_density'), ansagan_density=Sum('ansagan_density'),
                      agzu_fluid=Sum('agzu_fluid'), agzu_oil=Sum('agzu_oil'),
                      teh_rej_fluid=Sum('teh_rej_fluid'), teh_rej_oil=Sum('teh_rej_oil'))
        return Response(FieldBalanceSerializer(result, many=True).data)

    @action(methods=['post'], detail=False)
    def create_balance(self, request, *args, **kwargs):
        serializer = FieldBalanceCreateSerializer(data=request.data)
        if serializer.is_valid():
            field = models.Field.objects.get(name=request.data["field"])
            dt = datetime.now()
            balance = models.FieldBalance.objects.update_or_create(field=field, timestamp=dt,
                                                   defaults={"transport_balance": request.data["transport_balance"],
                                                             "transport_brutto": request.data["transport_brutto"],
                                                             "transport_netto": request.data["transport_netto"],
                                                             "transport_density": request.data["transport_density"]})
                                                             # "agzu_fluid": request.data["agzu_fluid"],
                                                             # "agzu_oil": request.data["agzu_oil"],
                                                             # "teh_rej_fluid": request.data["teh_rej_fluid"],
                                                             # "teh_rej_oil": request.data["teh_rej_oil"]})
            return Response(self.get_serializer(balance, many=False).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WellViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name',)
    queryset = models.Well.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.Well.objects.all()

    def get_serializer_class(self):
        return WellSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_field(self, request, *args, **kwargs):
        field = models.Field.objects.get(name=request.GET.get("field"))
        wells = models.Well.objects.filter(field=field)
        return Response(WellSerializer(wells, many=True).data)


class FieldViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name',)
    queryset = models.Field.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.Field.objects.all()

    def get_serializer_class(self):
        return FieldSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class TSViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('field',)
    queryset = models.TS.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.TS.objects.all()

    def get_serializer_class(self):
        return TSSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class GSMViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('field',)
    queryset = models.GSM.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.GSM.objects.all()

    def get_serializer_class(self):
        return GSMSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ProdProfileViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    queryset = models.ProdProfile.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.ProdProfile.objects.all()

    def get_serializer_class(self):
        return ProdProfileSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ImbalanceViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    queryset = models.Imbalance.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.Imbalance.objects.filter(imbalance__gte=7, imbalance__lte=80)

    def get_serializer_class(self):
        return ImbalanceSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def upload_dyn_data(request):
    try:
        for well in models.Well.objects.all():
            # well = models.Well.objects.get(name=request.data["well_name"])
            # dir = 'data/' + well.name
            dir = 'data/9030'
            for x in os.walk(dir):
                for day_folder in x[1]:
                    for y in os.walk(x[0] + '/' + day_folder):
                        timestamp = datetime.strptime(day_folder, '%Y_%m_%d')
                        for hour_folder in y[1]:
                            timestamp = timestamp + timedelta(hours=int(hour_folder))
                            skv_files = os.listdir(y[0] + '/' + hour_folder)
                            for skv_file in skv_files:
                                data = get_data.ReadSKVFile(y[0] + '/' + hour_folder + '/' + skv_file)
                                if len(data.x) > 0 and len(data.y) > 0:
                                    models.Dynamogram.objects.create(well=well, timestamp=timestamp, x=data.x, y=data.y)
                                    break
                break

        return Response({
            "info": "Данные загружены"
        })
    except:
        return Response({
            "info": "Скважина не найдена"
        })


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_dyn_data(request):
    well = models.Well.objects.get(name=request.GET.get('well_name'))
    dyn = models.Dynamogram.objects.filter(well=well).order_by('?').first()

    return Response(DynamogramSerializer(dyn).data)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_2hour(request):
    hour_data = dict()
    hour_data['EMG'] = dict()
    hour_data['EMG']['Общее'] = []
    hour_data['EMG']['UAZ'] = []
    hour_data['EMG']['PRORVA'] = []

    conn = pymysql.connect(host='192.168.17.158', port=3306, user='root', passwd='1234', db='emg-cm', charset='utf8')
    cur = conn.cursor()

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='2:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='2:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='4:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='4:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='6:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='6:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)
    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='8:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='8:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='10:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='10:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='12:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='12:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='14:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='14:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='16:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='16:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='18:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='18:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='20:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='20:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='22:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='22:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='0:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='0:00'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)

    all_temp = []
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='UAZ' and time='1:59'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp.append(float(row_values[i]))
        except:
            temp.append(0)
            all_temp.append(0)
    hour_data['EMG']['UAZ'].append(temp)
    temp = []
    cur.execute("SELECT * FROM n_2hour where oil_field='PRORVA' and time='1:59'")
    row_values = cur.fetchone()
    for i in range(3, 16):
        try:
            float(row_values[i])
            temp.append(float(row_values[i]))
            all_temp[i - 3] += float(row_values[i])
        except:
            temp.append(0)
    hour_data['EMG']['PRORVA'].append(temp)
    hour_data['EMG']['Общее'].append(all_temp)
    conn.close()
    return Response(hour_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def update_imbalance(request):
    wells = models.Well.objects.all()
    for well in wells:
        try:
            field = well.field.name
            if field == 'УАЗ' or field == 'Б.Жоламанова' or field == 'С.Котыртас' or field == 'Вос. Молдабек':
                conn = pymysql.connect(host='192.168.241.2', port=3306, user='getter', passwd='123456', db='sdmo',
                                       charset='utf8')
                cur = conn.cursor()
            elif field == 'Вос. Макат 2014' or field == 'М/р Алтыкуль' or field == 'Вос. Макат' or field == 'Ботахан':
                conn = pymysql.connect(host='192.168.243.2', port=3306, user='getter', passwd='123456', db='sdmo',
                                       charset='utf8')
                cur = conn.cursor()
            elif field == 'Жанаталап' or field == 'ЮВН' or field == 'ЮВК' or field == 'ЮЗК' or \
                    field == 'Салтанат Балгимбаева' or field == 'Гран':
                conn = pymysql.connect(host='192.168.236.2', port=3306, user='getter', passwd='123456', db='sdmo',
                                       charset='utf8')
                cur = conn.cursor()
            else:
                conn = pymysql.connect(host='192.168.128.2', port=3306, user='getter', passwd='123456', db='sdmo',
                                       charset='utf8')
                cur = conn.cursor()

            cur.execute("SELECT id FROM stations where code='" + well.name + "' limit 1")
            row_values = cur.fetchone()
            station_id = int(row_values[0])
            cur.execute("SELECT * FROM fc_data_last where reg=30005 and station_id=" + str(station_id) + " order by savetime desc")
            row_values = cur.fetchone()
            try:
                imb = models.Imbalance.objects.get(well=well)
                print("get")
            except:
                imb = models.Imbalance.objects.create(well=well)
                print("create")
            try:
                imb.imbalance = float(row_values[2])
            except:
                imb.imbalance = 0
            imb.timestamp = row_values[3]
            cur.execute("SELECT avg_1997 FROM daily_data where station_id=" + str(station_id) + " order by day desc limit 1")
            row_values = cur.fetchone()
            try:
                imb.avg_1997 = float(row_values[0])
            except:
                imb.avg_1997 = 0
            imb.save()

            conn.close()

        except Exception as e:
            pass

    return Response({
        "info": "Данные загружены"
    })

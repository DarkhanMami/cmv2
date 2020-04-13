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
    GSMSerializer, DynamogramSerializer, ImbalanceSerializer, ImbalanceHistorySerializer, ImbalanceHistoryAllSerializer, \
    SumWellInFieldSerializer, WellEventsSerializer, FieldMatrixSerializer
from django.core.mail import EmailMessage
from django.db.models import Sum, Avg
import cx_Oracle


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


class ImbalanceHistoryAll(generics.ListAPIView):
    queryset = models.ImbalanceHistoryAll.objects.all().order_by('timestamp')
    serializer_class = ImbalanceHistoryAllSerializer


class SumWellInFieldSerializerAll(generics.ListAPIView):
    queryset = models.SumWellInField.objects.all().order_by('timestamp')
    serializer_class = SumWellInFieldSerializer


class FieldMatrixSerializerAll(generics.ListAPIView):
    queryset = models.FieldMatrix.objects.all().order_by('timestamp')
    serializer_class = FieldMatrixSerializer


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
        return models.WellMatrix.objects.filter(timestamp=timezone.now(), well__has_isu=True)

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
    def get_all(self, request, *args, **kwargs):
        result = models.WellMatrix.objects.filter(timestamp=timezone.now())
        return Response(WellMatrixSerializer(result, many=True).data)

    @action(methods=['get'], detail=False)
    def get_by_well(self, request, *args, **kwargs):
        well = models.Well.objects.get(name=request.GET.get("well"))
        result = models.WellMatrix.objects.filter(well=well).order_by('timestamp')
        return Response(WellMatrixSerializer(result, many=True).data)

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


class WellEventsViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('well',)
    queryset = models.WellEvents.objects.all().order_by('-beg')[:100]

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.WellEvents.objects.all().order_by('-beg')[:100]

    def get_serializer_class(self):
        return WellEventsSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_well(self, request, *args, **kwargs):
        well = models.Well.objects.get(name=request.GET.get("well"))
        result = models.WellEvents.objects.filter(well=well).order_by('-beg')[:100]
        return Response(WellEventsSerializer(result, many=True).data)

    @action(methods=['get'], detail=False)
    def get_by_field(self, request, *args, **kwargs):
        field = models.Field.objects.get(name=request.GET.get("field"))
        result = models.WellEvents.objects.filter(well__field=field).order_by('-beg')[:100]
        return Response(WellEventsSerializer(result, many=True).data)


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

    @action(methods=['get'], detail=False)
    def get_with_events(self, request, *args, **kwargs):
        wells = models.Well.objects.filter(rem_count__gt=0)
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

    @action(methods=['get'], detail=True)
    def history(self, request, *args, **kwargs):
        imbalance = self.get_object()
        results = []
        for history in models.ImbalanceHistory.objects.filter(imb=imbalance):
            results.append(
              ImbalanceHistorySerializer(history).data
            )
        return Response(results)


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
    t = timezone.now()
    try:
        imbalance_history_all = models.ImbalanceHistoryAll.objects.get(timestamp__year=t.year, timestamp__month=t.month,
                                                                       timestamp__day=t.day)
        imbalance_history_all.count = 0
        imbalance_history_all.timestamp = timezone.now()
        imbalance_history_all.percent = 0
    except:
        imbalance_history_all = models.ImbalanceHistoryAll.objects.create(timestamp=timezone.now())
    for well in wells:
        try:
            if well.server == "192.168.241.2":
                conn = pymysql.connect(host='192.168.241.2', port=3306, user='getter', passwd='123456', db='sdmo',
                                       charset='utf8')
                cur = conn.cursor()
            elif well.server == "192.168.243.2":
                conn = pymysql.connect(host='192.168.243.2', port=3306, user='getter', passwd='123456', db='sdmo',
                                       charset='utf8')
                cur = conn.cursor()
            elif well.server == "192.168.236.2":
                conn = pymysql.connect(host='192.168.236.2', port=3306, user='getter', passwd='123456', db='sdmo',
                                       charset='utf8')
                cur = conn.cursor()
            elif well.server == "192.168.128.2":
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
                try:
                    timestamp = imb.timestamp + timedelta(hours=6)
                    if not row_values[3].strftime("%Y-%m-%d %H:%M:%S") == timestamp.strftime("%Y-%m-%d %H:%M:%S"):
                        imb_history = models.ImbalanceHistory.objects.create(imb=imb, well=imb.well, imbalance=imb.imbalance,
                                                                             avg_1997=imb.avg_1997, timestamp=imb.timestamp)
                        imb_history.save()
                except:
                    pass
            except:
                imb = models.Imbalance.objects.create(well=well)
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
            if imb.imbalance >= 7 and 80 >= imb.imbalance:
                imbalance_history_all.count += 1
             
            conn.close()
        except Exception as e:
            pass
    imbalance_history_all.percent = (imbalance_history_all.count / models.Well.objects.all().count()) * 100
    imbalance_history_all.save()
    return Response({
        "info": "Данные загружены"
    })


def update_well(wells, server):
    err_wells_server = list()
    for w in wells:
        try: 
            conn = pymysql.connect(host='192.168.17.158', port=3306, user='root', passwd='1234', db='emg-cm',
                                   charset='utf8')
            cur = conn.cursor()
            cur.execute("SELECT oil_field FROM n_well_matrix where well='" + w[0] + "'")
            row_values = cur.fetchone()
            if row_values is not None:
                print(w[0])
                print(row_values)
                try:
                    field = models.Field.objects.get(name=row_values[0])
                except:
                    field = models.Field.objects.create(name=row_values[0])
                try:
                    well = models.Well.objects.get(name=w[0],field=field)
                    print("get")
                except:
                    well = models.Well.objects.create(name=w[0],field=field)
                    print("create")
                well.well_id = w[1]
                well.server = server
                well.save()
            else:
                err_wells_server.append(w[0])
        except:
            err_wells_server.append(w[0])
    return err_wells_server


@api_view(['GET'])
def update_wells(request):
    err_sdmo_server = list()
    err_wells_server_all = list()
    try:
        conn = pymysql.connect(host='192.168.241.2', port=3306, user='getter', passwd='123456', db='sdmo',
                               charset='utf8')
        cur = conn.cursor()
        cur.execute("SELECT code,id FROM sdmo.stations")
        err_wells_server_all += update_well(cur.fetchall(), '192.168.241.2')
    except:
        err_sdmo_server.append('192.168.241.2')
    try:
        conn = pymysql.connect(host='192.168.243.2', port=3306, user='getter', passwd='123456', db='sdmo',
                               charset='utf8')
        cur = conn.cursor()
        cur.execute("SELECT code,id  FROM sdmo.stations")
        err_wells_server_all += update_well(cur.fetchall(), '192.168.243.2')
    except:
        err_sdmo_server.append('192.168.243.2')
    try:
        conn = pymysql.connect(host='192.168.236.2', port=3306, user='getter', passwd='123456', db='sdmo',
                               charset='utf8')
        cur = conn.cursor()
        cur.execute("SELECT code,id  FROM sdmo.stations")
        err_wells_server_all += update_well(cur.fetchall(), '192.168.236.2')
    except:
        err_sdmo_server.append('192.168.236.2')
    try:
        conn = pymysql.connect(host='192.168.128.2', port=3306, user='getter', passwd='123456', db='sdmo',
                               charset='utf8')
        cur = conn.cursor()
        cur.execute("SELECT code,id  FROM sdmo.stations")
        err_wells_server_all += update_well(cur.fetchall(), '192.168.236.2')
    except:
        err_sdmo_server.append('192.168.236.2')
    return Response({
        "info": "SUCCESS",
        "err_wells": err_wells_server_all,
        "err_sdmo_servers": err_sdmo_server
    })


# 11:50 or 11:30
@api_view(['GET'])
def update_sum_well(request):     
    for field in models.Field.objects.all(): 
        try:
            sum_well_in_field = models.SumWellInField.objects.get(field=field, timestamp=timezone.now())
        except:
            sum_well_in_field = models.SumWellInField.objects.create(field=field, timestamp=timezone.now())
            well_matrix = models.WellMatrix.objects.filter(timestamp=timezone.now(), well__field=field,
                                                           well__has_isu=True).aggregate(
                Avg('filling'), Sum('fluid_agzu'), Sum('fluid_isu'),
                Sum('teh_rej_fluid'), Sum('teh_rej_oil'), Avg('teh_rej_water'))

            sum_well_in_field.filling = well_matrix["filling__avg"]
            sum_well_in_field.fluid_agzu = well_matrix["fluid_agzu__sum"]
            sum_well_in_field.fluid_isu = well_matrix["fluid_isu__sum"]
            sum_well_in_field.teh_rej_fluid = well_matrix["teh_rej_fluid__sum"]
            sum_well_in_field.teh_rej_oil = well_matrix["teh_rej_oil__sum"]
            sum_well_in_field.teh_rej_water = well_matrix["teh_rej_water__avg"]
            sum_well_in_field.save()
    return Response({
        "message": "OK!"
    })


@api_view(['GET'])
def update_field_matrix(request):
    for field in models.Field.objects.all():
        try:
            field_matrix = models.FieldMatrix.objects.get(field=field, timestamp=timezone.now())
        except:
            field_matrix = models.FieldMatrix.objects.create(field=field, timestamp=timezone.now())
            well_matrix = models.WellMatrix.objects.filter(timestamp=timezone.now(), well__field=field).aggregate(
                Avg('filling'), Sum('fluid_agzu'), Sum('fluid_isu'),
                Sum('teh_rej_fluid'), Sum('teh_rej_oil'), Avg('teh_rej_water'))

            field_matrix.filling = well_matrix["filling__avg"]
            field_matrix.fluid_agzu = well_matrix["fluid_agzu__sum"]
            field_matrix.fluid_isu = well_matrix["fluid_isu__sum"]
            field_matrix.teh_rej_fluid = well_matrix["teh_rej_fluid__sum"]
            field_matrix.teh_rej_oil = well_matrix["teh_rej_oil__sum"]
            field_matrix.teh_rej_water = well_matrix["teh_rej_water__avg"]
            field_matrix.save()
    return Response({
        "message": "OK!"
    })


@api_view(['GET'])
def update_matrix(request):
    wells = models.Well.objects.all()
    err_emgcm_data = list()
    err_sdmo_data = list()
    # err_sdmo_server_all = list()
    for well in wells:
        try:
            well_matrix = models.WellMatrix.objects.get(timestamp=timezone.now(), well=well)
        except:
            well_matrix = models.WellMatrix.objects.create(timestamp=timezone.now(), well=well)
        try: 
            conn = pymysql.connect(host='192.168.17.158', port=3306, user='root', passwd='1234', db='emg-cm',
                                   charset='utf8')
            cur = conn.cursor()
            cur.execute("SELECT zamer, tr_fluid, tr_oil, tr_water FROM n_well_matrix where well='" + well.name + "'")
            row_values = cur.fetchone()
            if (row_values[0] is not None) and (row_values[1] is not None) and (row_values[2] is not None) and (row_values[3] is not None):
                well_matrix.fluid_agzu = row_values[0]
                well_matrix.teh_rej_fluid = row_values[1]
                well_matrix.teh_rej_oil = row_values[2]
                well_matrix.teh_rej_water = row_values[3]
            else:
                well_matrix.fluid_agzu = 0
                well_matrix.teh_rej_fluid = 0
                well_matrix.teh_rej_oil = 0
                well_matrix.teh_rej_water = 0
                err_emgcm_data.append(well.name)
        except:
            err_emgcm_data.append(well.name)

        if well.server == "192.168.241.2":
            try:
                conn = pymysql.connect(host='192.168.241.2', port=3306, user='getter', passwd='123456', db='sdmo',
                                       charset='utf8')
                cur = conn.cursor()
                cur.execute("SELECT avg_1997, debit_theoretical, no_work FROM sdmo.daily_data where station_id='"+str(well.well_id)+"' order by day desc limit 1")
                row_values = cur.fetchone()

                if (row_values[0] is not None) and (row_values[1] is not None) and (row_values[2] is not None):
                    well_matrix.filling = row_values[0]
                    well_matrix.fluid_isu = row_values[1]
                    well.well_stop += row_values[2] / 60
                    well.shortage_isu += well.well_stop * well_matrix.teh_rej_oil / 24 / 60
 
                else:
                    err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                    well_matrix.filling = 0 
                    well_matrix.fluid_isu = 0
            except:
                err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                well_matrix.filling = 0
                well_matrix.fluid_isu = 0
        elif well.server == "192.168.243.2":
            try:
                conn = pymysql.connect(host='192.168.243.2', port=3306, user='getter', passwd='123456', db='sdmo',
                                       charset='utf8')
                cur = conn.cursor()
                cur.execute("SELECT avg_1997,debit_theoretical,no_work FROM sdmo.daily_data where station_id='"+str(well.well_id)+"' order by day desc limit 1")
                row_values = cur.fetchone()
                if (row_values[0] is not  None) and (row_values[1] is not None) and (row_values[2] is not None):
                    well_matrix.filling = row_values[0]
                    well_matrix.fluid_isu = row_values[1]
                    well.well_stop += row_values[2] / 60
                    well.shortage_isu += well.well_stop * well_matrix.teh_rej_oil / 24 / 60
 
                else:
                    err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                    well_matrix.filling = 0 
                    well_matrix.fluid_isu = 0
            except:
                err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                well_matrix.filling = 0
                well_matrix.fluid_isu = 0
        elif well.server == "192.168.236.2":
            try:
                conn = pymysql.connect(host='192.168.236.2', port=3306, user='getter', passwd='123456', db='sdmo',
                                       charset='utf8')
                cur = conn.cursor()
                cur.execute("SELECT avg_1997,debit_theoretical,no_work FROM sdmo.daily_data where station_id='"+str(well.well_id)+"' order by day desc limit 1")
                row_values = cur.fetchone()
                if (row_values[0] is not None) and (row_values[1] is not None) and (row_values[2] is not None):
                    well_matrix.filling = row_values[0]
                    well_matrix.fluid_isu = row_values[1]
                    well.well_stop += row_values[2] / 60
                    well.shortage_isu += well.well_stop * well_matrix.teh_rej_oil / 24 / 60
 
                else:
                    err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                    well_matrix.filling = 0 
                    well_matrix.fluid_isu = 0
            except:
                err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                well_matrix.filling = 0
                well_matrix.fluid_isu = 0
        elif well.server == "192.168.128.2":
            try:
                conn = pymysql.connect(host='192.168.128.2', port=3306, user='getter', passwd='123456', db='sdmo',
                                       charset='utf8')
                cur = conn.cursor()
                cur.execute("SELECT avg_1997,debit_theoretical,no_work FROM sdmo.daily_data where station_id='"+str(well.well_id)+"' order by day desc limit 1")
                row_values = cur.fetchone()
                if (row_values[0] is not None) and (row_values[1] is not None) and (row_values[2] is not None):
                    well_matrix.filling = row_values[0]
                    well_matrix.fluid_isu = row_values[1]
                    well.well_stop += row_values[2] / 60
                    well.shortage_isu += well.well_stop * well_matrix.teh_rej_oil / 24 / 60
 
                else:
                    err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                    well_matrix.filling = 0 
                    well_matrix.fluid_isu = 0
            except:
                err_sdmo_data.append('NAME:'+str(well.name)+' ID:'+str(well.well_id))
                well_matrix.filling = 0
                well_matrix.fluid_isu = 0
        well_matrix.save()
        well.save()
    return Response({
        "info": "SUCCESS",
        "err_staition_teh_rej_null": err_emgcm_data,
        "err_sdmo_data":err_sdmo_data  
    })


@api_view(['GET'])
def update_events(request):
    con = cx_Oracle.connect('integration_EMG/integra@172.20.10.220/orcl', encoding='UTF-8', nencoding='UTF-8')
    cur = con.cursor()
    wells = models.Well.objects.all()
    for well in wells:
        cur.execute("SELECT * FROM WELL_REPAIR_ACT_TRANSFER where WELL_ID=" + str(well.tbd_id)
                    + " and DBEG > to_date('2019-12-31','yyyy-MM-dd')")

        transfers = cur.fetchall()
        rem_count = 0
        well_stop = 0
        shortage_prs = 0

        for transfer in transfers:
            rem_count += 1
            beg_id = transfer[0]
            beg = transfer[4]
            rem_name = transfer[5]
            if int(transfer[2] == 1):
                rem_type = 'КРС'
            elif int(transfer[2] == 2):
                rem_type = 'ТРС'
            elif int(transfer[2] == 3):
                rem_type = 'ПРС'
            else:
                rem_type = 'Прочие простои'

            cur.execute("SELECT * FROM WELL_REPAIR_ACT_RETURN where WELL_REPAIR_ACT_TRANSFER_ID=" + str(beg_id))
            act_return = cur.fetchone()
            if act_return:
                end = act_return[2]

            hours = 0
            if end > beg:
                diff = end - beg
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600

            well_stop += hours / 24

            cur.execute("SELECT * FROM REPAIR_WORK_TYPE where ID=" + str(rem_name))
            work_type = cur.fetchone()
            if work_type:
                event = work_type[1]

            got, created = models.WellEvents.objects.get_or_create(well=well, event_type=rem_type, event=event,
                                                                   beg=beg, end=end)
            if created:
                cur.execute("SELECT * FROM TECH_MODE where WELL_ID=" + str(well.tbd_id)
                            + " and DBEG < to_date('" + beg.strftime('%Y-%m-%d') + "','yyyy-MM-dd')"
                            + " and DEND > to_date('" + beg.strftime('%Y-%m-%d') + "','yyyy-MM-dd')"
                            + " and DBEG > to_date('2019-01-01','yyyy-MM-dd')")
                oil = cur.fetchone()
                if oil:
                    shortage_prs += oil[6] * hours / 24

        well.rem_count = rem_count
        well.well_stop_prs = well_stop
        well.shortage_prs += shortage_prs
        well.save()

    con.close()

    return Response({
        "info": "Данные загружены"
    })

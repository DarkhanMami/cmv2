from django.db.models import QuerySet
from rest_framework import serializers

from api.serializers import UserSerializer
from main.models import *


class EmptySerializer(serializers.Serializer):
    pass


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['name', 'pk']


class PrsDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrsDevice
        fields = ['num']


class WellSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=False, read_only=True)

    class Meta:
        model = Well
        fields = ['name', 'field', 'well_id', 'tbd_id', 'server', 'production_type', 'has_isu', 'shortage_isu', 'tpn',
                  'pump_depth', 'shortage_prs', 'well_stop_prs', 'well_stop', 'rem_count', 'gzu', 'horizon']


class WellMatrixSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = WellMatrix
        fields = ['well', 'filling', 'fluid_agzu', 'teh_rej_fluid', 'teh_rej_oil', 'teh_rej_water', 'fluid_isu',
                  'park_fluid', 'park_oil', 'kpn', 'tbd_fluid', 'p_zab', 'p_plast', 'dyn_level', 'sdmo_status',
                  'status', 'pump_speed', 'electric_cons', 'timestamp']


class DepressionSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = Depression
        fields = ['well', 'densityPL', 'densityZB', 'densityDiff', 'fluid_av', 'timestamp']


class WellMatrixCreateSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = WellMatrix
        fields = ['well', ]


class WellEventsSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = WellEvents
        fields = ['well', 'event_type', 'event', 'beg', 'end']


class RecommendationSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = Recommendation
        fields = ['well', 'kpn', 'event', 'timestamp']


class FieldBalanceSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=False, read_only=True)

    class Meta:
        model = FieldBalance
        fields = ['field', 'transport_balance', 'ansagan_balance', 'transport_brutto', 'ansagan_brutto',
                  'transport_netto', 'ansagan_netto', 'transport_density', 'ansagan_density',
                  'agzu_fluid', 'agzu_oil', 'teh_rej_fluid', 'teh_rej_oil', 'timestamp']


class FieldBalanceCreateSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=False, read_only=True)

    class Meta:
        model = FieldBalance
        fields = ['field', 'transport_balance', 'transport_brutto', 'transport_netto', 'transport_density']


class TSSerializer(serializers.ModelSerializer):

    class Meta:
        model = TS
        fields = ['gos_num', 'marka', 'type', 'total_days', 'in_work', 'in_rem', 'day_off',
                  'month', 'year', 'field', 'kip', 'ktg']


class GSMSerializer(serializers.ModelSerializer):

    class Meta:
        model = GSM
        fields = ['gos_num', 'type', 'year', 'month', 'field', 'gsm_type', 'sum', 'quantity']


class ProdProfileSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = ProdProfile
        fields = ['well', 'well_pair', 'pre_fluid', 'post_fluid', 'pre_oil', 'post_oil', 'pre_obv', 'post_obv', 'effect']


class DynamogramSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dynamogram
        fields = ['well', 'x', 'y', 'timestamp']


class WattmetrogramSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wattmetrogram
        fields = ['well', 'x', 'y', 'timestamp']


class ImbalanceSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = Imbalance
        fields = ['id', 'well', 'imbalance', 'avg_1997', 'timestamp']


class ImbalanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Imbalance
        fields = [ 'imbalance', 'avg_1997', 'timestamp']


class ImbalanceHistoryAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImbalanceHistoryAll
        fields = [ 'count', 'percent', 'timestamp']


class SumWellInFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = SumWellInField
        fields = '__all__'


class FieldMatrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldMatrix
        fields = '__all__'


class ConstantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Constant
        fields = '__all__'


class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = '__all__'

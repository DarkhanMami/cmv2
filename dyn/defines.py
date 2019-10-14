# -*- coding: utf-8 -*-
from collections import namedtuple
from collections import OrderedDict as od


DEBUG = True
COM1 = 0
COM2 = 1
COM3 = 2
COM4 = 3
COM5 = 4
COM6 = 5

DNMK = 'DNMK'
DDS = 'DDS'

DYNAMOMETER_PACKET_LEN = 26
RESPONSE_TIMEOUT = 10
LOG_FILE_NAME = "/var/log/isu/dynamometer.log"
DIAGNOSTIC_LIB = "/usr/local/lib/diagnostic.so"
SKV_FILES_PATH = "/var/isu/skv/"
ARCHIVE_STORE_DAYS = 30

SENSOR_FAILURE = 1
SENSOR_IN_WORK = 0

SAVE_TO_LOG_PERIOD = 5

MAX_DIN = 4032

# ========== Static data SKV file ========== #
SkvStaticData = od()
SkvStaticData['SkvStaticData'] = {
    'struct': '<8si16s16sd47f4s12s12s24s4s',
    'namedtuple': namedtuple('header1', 'VerSkv kolBlock aNumSkv aNumKust DateEtalon '
                                        'H d ReservS3 ReservS4 ReservS5 '
                                        'RoOil RoWater ReservS0 nkt089 nkt073 '
                                        'nkt060 kol025 kol022 kol019 kol016 '
                                        'f089 f073 f060 f025 f022 '
                                        'f019 f016 SigmaDop kol028 f028 '
                                        'kol032 f032 ax ay bx '
                                        'by cx cy dx dy '
                                        'RoSteel ESteel KEtDeb DebitEt ReservPS1 '
                                        'ReservPS2 ReservPS3 ReservPS4 ReservPS5 ReservPS6 '
                                        'ReservPS7 ReservPS8 ReservPB ReservSt typeH typeCK ykazEnd1'),
    'dict': 0
}

# ========== Block data SKV file ========== #
SkvBlock = od()
SkvBlock['DataSkvKust'] = {
    'struct': '<d10i14f5s6s5s8s',
    'namedtuple': namedtuple('S_TdataSkvKust', 'aDateWork hm Pn Pv numOKr PtUp '
                                         'PtDn LHoda PtStat TypeOfDevice DltStat '
                                         'LHodaX1 LHodaX2 LHodaPlX1 LHodaPlX2 LHodaX3 '
                                         'LHodaPlX3 obvod K2DeGaz Pu Pz '
                                         'K_GERM K_UT_NAS R Qtexnol HGDY '
                                         'Ispolnit ReservSt ReserB'),
    'dict': 0
}
SkvBlock['Data'] = {
    'struct': '<%sf' % MAX_DIN,
    'array': [0]*2*MAX_DIN
}
SkvBlock['header_end'] = {
    'struct': '<32s4s',
    'namedtuple': namedtuple('header2', 'operatorName ykazEnd2'),
    'dict': 0
}

# ==========  ==========#
blockData = [0]*2*MAX_DIN


# ========== Par skv kust ==========#
parSkv = {
    'len': [0]*24,
    'struct': '<24f',
    'namedtuple': namedtuple('outData', 'H d nkt089 nkt073 nkt060 '
                                        'nkt048 kol032 kol028 kol025 kol022 '
                                        'kol019 kol016 f089 f073 f060 '
                                        'f048 f032 f028 f025 f022 '
                                        'f019 f016 ESteel KPD')
}

# ========== Data SKV file ==========#
datSkv = {
    'len': [0]*9,
    'struct': '9i',
    'namedtuple': namedtuple('outData', 'PtUp PtDn LHoda R TypeOfDevice '
                                        'K2DeGaz dax PtU PtD')
}

# ========== Out data ==========#
outDebit = {
    'len': [0]*11,
    'struct': '<11f',
    'namedtuple': namedtuple('outData', 'QTeor QFact LHodaX1 LHodaX2 LHodaX3 '
                                        'LHodaY1 LHodaY2 LHodaY3 Ay By Bx'),
    'dict': 0
}

# ========== Out koef ==========#
outKoef = {
    'len': [0]*18,
    'struct': '<18f',
    'namedtuple': namedtuple('outKoef', 'K1 '
                                        'norm '
                                        'late_valve_down '
                                        'push_valve_leak '
                                        'suction_valve_leak '
                                        'gas_effect '
                                        'insufficient_flow '
                                        'upper_point_leak '
                                        'lower_point_leak '
                                        'pump_plunger_out '
                                        'plunger_upper_point_stuck '
                                        'plunger_lower_point_stuck '
                                        'plunger_end_way_stuck '
                                        'fontain_or_broken_plunger '
                                        'tube_pump '
                                        'insertion_pump '
                                        'paraphene '
                                        'flood'),
    'dict': 0
}
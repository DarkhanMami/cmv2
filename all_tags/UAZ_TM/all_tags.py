import pymysql
from pyModbusTCP.client import ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from all_tags.UAZ_TM import tags


def update_tags():
    c = ModbusClient(host="192.168.241.77", port=502, auto_open=True)

    conn = pymysql.connect('192.168.17.158', port=3306, user='root', passwd='1234', db='emg-cm')
    cur = conn.cursor()
    c.open()

    data = dict()

    for tag in tags.tags:
        reg = tags.tags[tag]
        regs = None
        for i in range(5):
            regs = c.read_holding_registers(reg, 2)
            if regs:
                break
        if regs:
            decoder = BinaryPayloadDecoder.fromRegisters(regs, Endian.Big, wordorder=Endian.Big)
            if reg > 21:
                value = decoder.decode_16bit_uint()
            else:
                value = decoder.decode_32bit_float()

            quan = cur.execute("SELECT * FROM n_wincctags where tag_key='" + tag + "' and oil_field = 'UAZ'")
            data[tag] = value

            if quan == 0:
                sql = ("INSERT INTO n_wincctags(oil_field, tag_key, tag_value, last_update) VALUES('UAZ', '{0}', '{1}', now())").format(tag, value)
                cur.execute(sql)
            else:
                sql = ("UPDATE n_wincctags SET tag_value='{0}',last_update=now() WHERE tag_key='{1}' and oil_field='UAZ'").format(value, tag)
                cur.execute(sql)

    skv1 = 'UAZ_'
    skv2 = 'UAZ_'
    skv3 = 'UAZ_'
    skv4 = 'UZV_'
    skv5 = 'UAZ_'

    val1 = str(data['OP_MU001_ARCH_Debit_zhidk_m3'])
    val2 = str(data['KABBSK_MU002.DR_Q_CONS_FLOW'])
    val3 = str(data['KABBSK_MU003_IMP.RO_Q_CONS_FLOW'])
    val4 = str(data['KABBSK_MU004_IMP.RO_Q_CONS_FLOW'])
    val5 = str(float(data['KABBSK_MU005_IMP.RO_Q_CONS_FLOW']) / 10)

    tmp_skv = int(data['OP_MU001_ARCH_Code_SKV1'])
    if tmp_skv < 10:
        skv1 = skv1 + '000' + str(tmp_skv)
    elif tmp_skv < 100:
        skv1 = skv1 + '00' + str(tmp_skv)
    elif tmp_skv < 1000:
        skv1 = skv1 + '0' + str(tmp_skv)

    tmp_skv = int(data['KABBSK_MU002.DR_N_WELL'])
    if tmp_skv < 10:
        skv2 = skv2 + '000' + str(tmp_skv)
    elif tmp_skv < 100:
        skv2 = skv2 + '00' + str(tmp_skv)
    elif tmp_skv < 1000:
        skv2 = skv2 + '0' + str(tmp_skv)

    tmp_skv = int(data['KABBSK_MU003_IMP.RO_N_WELL'])
    if tmp_skv < 10:
        skv3 = skv3 + '000' + str(tmp_skv)
    elif tmp_skv < 100:
        skv3 = skv3 + '00' + str(tmp_skv)
    elif tmp_skv < 1000:
        skv3 = skv3 + '0' + str(tmp_skv)

    tmp_skv = int(data['KABBSK_MU005_IMP.RO_N_WELL'])
    if tmp_skv < 10:
        skv5 = skv5 + '000' + str(tmp_skv)
    elif tmp_skv < 100:
        skv5 = skv5 + '00' + str(tmp_skv)
    elif tmp_skv < 1000:
        skv5 = skv5 + '0' + str(tmp_skv)

    tmp_skv = int(data['KABBSK_MU004_IMP.RO_N_WELL'])
    if tmp_skv < 10:
        skv4 = skv4 + '00' + str(tmp_skv) + 'U'
    elif tmp_skv < 100:
        skv4 = skv4 + '0' + str(tmp_skv) + 'U'
    elif tmp_skv < 1000:
        skv4 = skv4 + '0' + str(tmp_skv)

    if skv4 == "UZV_007U":
        cur.execute("update n_well_matrix set zamer = " + val4 + " where well = 'UZV_0103';")
    if skv4 == "UZV_0103":
        cur.execute("update n_well_matrix set zamer = " + val4 + " where well = 'UZV_007U';")
    if skv4 == "UZV_0107":
        cur.execute("update n_well_matrix set zamer = " + val4 + " where well = 'UZV_0111';")
    if skv4 == "UZV_0111":
        cur.execute("update n_well_matrix set zamer = " + val4 + " where well = 'UZV_0107';")
    if skv4 == "UZV_003U":
        cur.execute("update n_well_matrix set zamer = " + val4 + " where well = 'UZV_0108';")
    if skv4 == "UZV_0108":
        cur.execute("update n_well_matrix set zamer = " + val4 + " where well = 'UZV_003U';")

    cur.execute("update n_well_matrix set zamer = " + val1 + " where well = '" + skv1 + "';")
    cur.execute("update n_well_matrix set zamer = " + val2 + " where well = '" + skv2 + "';")
    cur.execute("update n_well_matrix set zamer = " + val3 + " where well = '" + skv3 + "';")
    cur.execute("update n_well_matrix set zamer = " + val5 + " where well = '" + skv5 + "';")

    conn.commit()
    conn.close()
    c.close()

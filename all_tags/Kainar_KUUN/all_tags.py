import pymysql
from pyModbusTCP.client import ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian


def update_tags():
    c = ModbusClient(host="192.168.207.242", port=502, auto_open=True)

    conn = pymysql.connect('192.168.17.158', port=3306, user='root', passwd='1234', db='emg-cm')
    cur = conn.cursor()
    c.open()

    tags = {
        'FLOW/MASS1/OUT.CV': 1,
        'FLOW/DENS1/OUT.CV': 3,
        'FLOW/TEMP1/OUT.CV': 5,
        'FLOW/PRESS1/OUT.CV': 7,
        'FLOW/MASS2/OUT.CV': 9,
        'FLOW/DENS2/OUT.CV': 11,
        'FLOW/TEMP2/OUT.CV': 13,
        'FLOW/PRESS2/OUT.CV': 15,
        'BATCH_A/SS_MASS_T/OUT.CV': 17,
        'CUR_DATA/TOT_M/OUT.CV': 19,
        'BATCH_A/CUR_MAS/OUT.CV': 21,
        'BATCH_A/SS_MASS_T_L1/OUT.CV': 23,
        'CUR_DATA/TOT_M1/OUT.CV': 25,
        'BATCH_A/CUR_MAS_L1/OUT.CV': 27,
        'BATCH_A/SS_MASS_T_L2/OUT.CV': 29,
        'CUR_DATA/TOT_M2/OUT.CV': 31,
        'BATCH_A/CUR_MAS_L2/OUT.CV': 33,
        'CUR_DATA/MASS_M/OUT.CV': 35,
        'DATA_A/MASS_M.CV': 37,
        'FLOW/MASS/OUT.CV': 39,
        'FLOW/TEMP3/OUT.CV': 41,
        'FLOW/PRESS3/OUT.CV': 43
    }

    for tag in tags:
        reg = tags[tag]
        regs = None
        for i in range(5):
            regs = c.read_holding_registers(reg, 2)
            if regs:
                break
        if regs:
            decoder = BinaryPayloadDecoder.fromRegisters(regs, Endian.Big, wordorder=Endian.Big)
            value = decoder.decode_32bit_float()

            quan = cur.execute("SELECT * FROM n_wincctags where tag_key='" + tag + "' and oil_field = 'Kainar_KUUN'")
            if quan == 0:
                sql = ("INSERT INTO n_wincctags(oil_field, tag_key, tag_value, last_update) VALUES('Kainar_KUUN', '{0}', '{1}', now())").format(tag, value)
                cur.execute(sql)
            else:
                sql = ("UPDATE n_wincctags SET tag_value='{0}',last_update=now() WHERE tag_key='{1}' and oil_field='Kainar_KUUN'").format(value, tag)
                cur.execute(sql)
    c.close()

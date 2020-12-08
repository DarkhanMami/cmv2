import pymysql
from pyModbusTCP.client import ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from all_tags.Karsak_KUUN import tags


def update_tags():
    c = ModbusClient(host="192.168.200.73", port=502, auto_open=True)

    conn = pymysql.connect('192.168.17.158', port=3306, user='root', passwd='1234', db='emg-cm')
    cur = conn.cursor()
    c.open()

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

            quan = cur.execute("SELECT * FROM n_wincctags where tag_key='" + tag + "' and oil_field = 'Karsak_KUUN'")
            if quan == 0:
                sql = ("INSERT INTO n_wincctags(oil_field, tag_key, tag_value, last_update) VALUES('Karsak_KUUN', '{0}', '{1}', now())").format(tag, value)
                cur.execute(sql)
            else:
                sql = ("UPDATE n_wincctags SET tag_value='{0}',last_update=now() WHERE tag_key='{1}' and oil_field='Karsak_KUUN'").format(value, tag)
                cur.execute(sql)

    conn.commit()
    conn.close()
    c.close()

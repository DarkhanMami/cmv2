import pymysql, OpenOPC
import datetime, traceback, smtplib

try:
    conn = pymysql.connect('localhost', port=3306, user='root', passwd='1234', db='emg-cm')
    cur = conn.cursor()

    A = open('tags.txt', 'r')
    tags = A.read().splitlines()
    A.close()
    opc = OpenOPC.open_client('192.168.207.178')

    opc.connect(u'OPCServer.WinCC.1')

    # try:
    Data = opc.read(tags, group='test', timeout=100000)
    # except:
    # 	print('timeOut')
    opc.remove('test')
    for i in Data:
        # print(i)
        tag = i[0]
        value = i[1]
        quality = i[2]
        update_date = i[3]
        # print(tag,update_date)
        try:
            update_date = datetime.datetime.strptime(update_date, '%m/%d/%y %H:%M:%S')  # 06/05/19 18:19:48
        # print(update_date)
        except:
            # print('Error')
            pass
            update_date = datetime.datetime.now()
        quan = cur.execute("SELECT * FROM n_wincctags where tag_key='" + tag + "' and oil_field = 'UAZ'")
        if (quan == 0):
            Sql = (
                "INSERT INTO n_wincctags(oil_field, tag_key, tag_value, last_update) VALUES('UAZ','{0}','{1}',now())").format(
                tag, value)
            # print(Sql)
            # if(quality=='Good'):
            cur.execute(Sql)
        else:
            Sql = (
                "UPDATE n_wincctags SET tag_value='{0}',last_update=now(),last_actual_update='{1}' WHERE tag_key='{2}' and oil_field='UAZ'").format(
                value, update_date, tag)
            # print(Sql)
            # if(quality=='Good'):
            cur.execute(Sql)

    conn.commit()
    conn.close()
    opc.close()
    C = open('numberOfRetries.txt', 'r')
    numberOfRetries = int(C.read())
    C.close()
    numberOfRetries = 0
except:
    B = open("log.txt", "a")
    C = open('all_tags/Moldabek/numberOfRetries.txt', 'r')
    numberOfRetries = int(C.read())
    C.close()
    # print(numberOfRetries)
    B.write(str(datetime.datetime.now()))
    traceback.print_exc(file=B)
    # traceback.print_exc(file=sys.stdout)
    B.write('\n')
    print("Finished incorrectly")
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    send_to = ['Y.Tlegenov@emg.kmgep.kz',]  #
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.ehlo()
    smtpObj.login("noreply@dlc.kz", "Emb@2019")
    if (numberOfRetries > 20):
        smtpObj.sendmail('noreply@dlc.kz', send_to, 'Timeout occured or opc server(UAZ) is unavailable')
        numberOfRetries = 0
    C = open('numberOfRetries.txt', 'w')
    C.write(str(numberOfRetries + 1))
    C.close()
    smtpObj.close()
    B.close()
    # conn.close()
    # opc.close()


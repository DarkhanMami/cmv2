import pymysql
import datetime, traceback, smtplib
import sys
sys.path.append("/webapps/cmv2/OpenOPC/src/")
import OpenOPC


try:
    conn = pymysql.connect('192.168.17.158', port=3306, user='root', passwd='1234', db='emg-cm')
    cur = conn.cursor()

    A = open('tags.txt', 'r')
    tags = A.read().splitlines()
    A.close()
    opc = OpenOPC.open_client('192.168.207.178')

    opc.connect(u'OPCServer.WinCC.1')
    tmp = opc.read(tags, group='test', timeout=100000)
    data = dict()
    for i in tmp:
        data[i[0]] = [i[1], i[2], i[3]]
    opc.remove('test')
    opc.close()
    for i in range(0, 51):
        tag_skv = 'KABBVM_MU' + str(i) + '.Code_SKV1'
        tag_debit = 'KABBVM_MU' + str(i) + '.Debit'
        if tag_skv in data:
            skv = 'VMB_'
            tmp = int(data[tag_skv][0])
            update_date = data[tag_debit][2]
            debit = data[tag_debit][0]
            if tmp < 10:
                skv += '000' + str(tmp)
            elif 10 <= tmp < 100:
                skv += '00' + str(tmp)
            elif 100 <= tmp < 1000:
                skv += '0' + str(tmp)
            elif 1000 <= tmp:
                skv += str(tmp)

            try:
                update_date = datetime.datetime.strptime(update_date, '%m/%d/%y %H:%M:%S')
            except:
                update_date = datetime.datetime.now()
            cur.execute("update n_well_matrix set debit = " + str(debit) + "oil_field = 'VMB' and well = '" + skv + "'")

    conn.commit()
    conn.close()
    C = open('numberOfRetries.txt', 'r')
    numberOfRetries = int(C.read())
    C.close()
    numberOfRetries = 0
except Exception as e:
    print(e)

    B = open("log.txt", "a")
    C = open('numberOfRetries.txt', 'r')
    numberOfRetries = int(C.read())
    C.close()
    B.write(str(datetime.datetime.now()))
    traceback.print_exc(file=B)
    B.write('\n')
    print("Finished incorrectly")
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    send_to = ['Y.Tlegenov@emg.kmgep.kz',]
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.ehlo()
    smtpObj.login("noreply@dlc.kz", "Emb@2019")
    if numberOfRetries > 20:
        smtpObj.sendmail('noreply@dlc.kz', send_to, 'Timeout occured or opc server(VMB) is unavailable')
        numberOfRetries = 0
    C = open('numberOfRetries.txt', 'w')
    C.write(str(numberOfRetries + 1))
    C.close()
    smtpObj.close()
    B.close()
    conn.close()
    opc.close()


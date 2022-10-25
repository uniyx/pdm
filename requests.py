import psycopg2


def print_request(connection, UID):
    con = connection
    print("1 if you wish to make a request/n2 if you wish to complete an existing request")
    val = input("Please make your selection")
    if val == 1:
        barcode = input("Please enter the barcode of the item you want to borrow")
        datereq = input("please input the date you require the tool by")
        returndate = input("please input the date you will return the tool by")
        # needs catalogue to operate
        # cur = con.cursor()
        # cur.execute("select uid from catalogue where barcode = %s ", barcode)
        make_request(con, UID, "temp", barcode, datereq, returndate)
        con.close()
    else:
        barcode = input("please enter the barcode of the item you wish to return")
        request_completed(con, "temp", "temp", barcode)
        con.close()


def make_request(con, requester, requestee, barcode, daterequired, returnbydate):
    cur = con.cursor()
    cur.execute('select shareable, shared from tools where barcode = %i', barcode)
    rows = cur.fetchall()
    if rows[0] == False:
        return 'Tool not shareable'
    elif rows[1] == True:
        return 'Tool currently being shared'
    cur.execute("update tools set shared = true where barcode = %i", barcode)
    cur.execute("select max(rid) from requests")
    rows = cur.fetchall()
    rid = rows[0]
    cur.execute("insert into requests (rid, barcode, daterequired, status, returnbydate, requester, requestee) values "
                "(%i, %i, %s, 0 %s,%s, %s)", rid, barcode, daterequired, returnbydate, requester, requestee)
    con.commit()
    # update catalogue once that's implamented
    cur.close()
    con.close()
    return 'Tool Successfully Shared'


def request_completed(con, requester, requestee, barcode):
    cur = con.cursor()
    cur.execute("update tools set shared = false where barcode = %i", barcode)
    cur.execute("update requests set status = 1 where barcode = %i", barcode)
    cur.close()

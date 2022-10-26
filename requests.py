import psycopg2

def print_request(connection, UID):
    con = connection

    print("----------------------------------------")
    print("1. Create request")
    print("2. Complete an existing request")
    val = input("Select: ")

    if val == 1:
        print("Enter the barcode of the item you want to borrow")
        barcode = input("Barcode: ")
        print("Enter the date you require the tool by")
        datereq = input("Date: ")
        print("Enter the date the tool will be returned")
        returndate = input("Return Date")
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
    cur.execute('select shareable, shared from tools where barcode = %s', barcode)
    rows = cur.fetchall()
    if rows[0] == False:
        return 'Tool not shareable'
    elif rows[1] == True:
        return 'Tool currently being shared'
    cur.execute("update tools set shared = true where barcode = %s", barcode)
    cur.execute("select max(rid) from requests")
    rows = cur.fetchall()
    rid = rows[0]
    cur.execute("insert into requests (rid, barcode, daterequired, status, returnbydate, requester, requestee) values "
                "(%s, %s, %s, 0 %s,%s, %s)", rid, barcode, daterequired, returnbydate, requester, requestee)
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

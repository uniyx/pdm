import psycopg2


# cur = con.cursor()
# cur.execute("select id, name from employees")
# rows = cur.fetchall()
# for r in rows:
#   print("id {r[0]} name {r[1]}")
# cur.execute("insert into employees (id, name) values (%s, %s)", (id1, name1)
# con.commit()
# cur.close()
# con.close()
def print_request(connection):
    con = connection


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
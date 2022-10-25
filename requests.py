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


def make_request(connection, requester, requestee, barcode):
    con = connection
    user = requester  # intended for use once catalogue is implamented
    other = requestee  # intended for use once catalogue is implamented
    cur = con.cursor()
    cur.execute('select shareable, shared from tools where barcode = %i', barcode)
    rows = cur.fetchall()
    if rows[0] == False:
        return 'Tool not shareable'
    elif rows[1] == True:
        return 'Tool currently being shared'
    cur.execute("update tools set shareable = false shared = true where barcode = %i", barcode)
    # update catalogue once that's implamented
    cur.close()
    con.close()
    return 'Tool Successfully Shared'


def request_completed(connection):
    temp = False

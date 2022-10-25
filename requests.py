import psycopg2
#cur = con.cursor()
#cur.execute("select id, name from employees")
#rows = cur.fetchall()
# for r in rows:
#   print("id {r[0]} name {r[1]}")
#cur.execute("insert into employees (id, name) values (%s, %s)", (id1, name1)
#con.commit()
#cur.close()
#con.close()
def print_request():

def make_request(connection, requester, requestee, barcode):
    con = connection
    user = requester
    other = requestee
    cur = con.cursor()
    cur.execute('select shareable from tools where barcode = %s', barcode)
    rows = cur.fetchall()
    if (rows[0] == 'false'):
        return False
    cur.execute("update tools set shareable = 'false' ")

def request_completed(connection):
from datetime import date, datetime
import psycopg2
from sshtunnel import SSHTunnelForwarder
from datetime import datetime, timezone

# get params
with open('params.txt') as file:
    params = file.readlines()
    params = [line.rstrip() for line in params]

# Create SSH Tunnel
server = SSHTunnelForwarder(
    ('starbug.cs.rit.edu', 22),
    ssh_username = params[2],
    ssh_password = params[3],
    remote_bind_address = (params[0], 5432)
)

server.start()
print("Server connected on " + str(server.local_bind_port))

# connect to the db
paramspg = {
    "host": params[0],
    "port": server.local_bind_port,
    "database": params[1],
    "user": params[2],
    "password": params[3]
}

con = psycopg2.connect(**paramspg)

print("Database connected")

# cursors talk to the database
cur = con.cursor()

# get current uid
cur.execute("select uid from users")
uids = [r[0] for r in cur.fetchall()]
uid = uids[-1] + 1

# add user
d = date.today()
dt = datetime.now()
SQL = "INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
data = (uid, "uni@esteves.net", "uniyx", "cum", "gian", "esteves", d, dt)
cur.execute(SQL, data)

# execute query
cur.execute("select uid, firstname, lastname from users")

# gets an array of tuples
rows = cur.fetchall()

print(rows)

for r in rows:
    print(f"id: {r[0]} name: {r[1]}")

# save changes
con.commit()

# close the cursor
cur.close()

# close the connection
con.close()
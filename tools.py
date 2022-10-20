from datetime import date, datetime
import psycopg2
from sshtunnel import SSHTunnelForwarder
from datetime import datetime

# get params
with open('params.txt') as file:
    params = file.readlines()
    params = [line.rstrip() for line in params]

# Create SSH Tunnel

def sshtunnel():
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
    # cursors talk to the database
    # cur = con.cursor()

    print("Database connected")
    return con

#def exit():
#    # save changes
#    con.commit()
#
    # close the cursor
#    cur.close()
#
    # close the connection
#    con.close()

#    print("Exited.")
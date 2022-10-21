"""
cli.py, Command line interface for PDM Tools Database
Author: Gian Esteves
"""

from unicodedata import category
from tools import *

def main():
    global con
    con = sshtunnel()
    global curruser
    print_signin()

def print_signin():
    print("----------------------------------------")
    print("1. Login")
    print("2. Create an account")
    print("3. Exit")
    print("----------------------------------------")

    val = input("Select: ")
    match int(val):
        case 1:
            print_login()
        case 2:
            print_createacc()
        case 3:
            print("Exiting...")
            exit()
        case default:
            print_signin()

def print_login():
    print("----------------------------------------")
    username = input("Username: ")

    # Find if user exists
    cur = con.cursor()
    cur.execute("SELECT username FROM users")

    # gets an array of tuples
    users = [r[0] for r in cur.fetchall()]
    #print(users)

    if username not in users:
        print("Could not find user")
        print_login()

    # Proceed if user exists
    password = input("Password: ")
    SQL = "SELECT password, uid, lastaccess FROM users WHERE username = %s"
    data = (username,)
    cur.execute(SQL, data)
    results = cur.fetchall()

    realpassword = [r[0] for r in results][0]
    uid = [r[1] for r in results][0]
    #lastaccess = [r[2] for r in results][0]

    if password == realpassword:
        print("Successfully logged in as {} ({}).".format(username, uid))
    else:
        print("Wrong password. Try again.")
        print_login()

    # record access time
    lastaccess = datetime.now()
    SQL = "UPDATE users SET lastaccess = %s WHERE uid = %s"
    data = (lastaccess, uid)
    cur.execute(SQL, data)

    # close cursor
    con.commit()
    cur.close()

    # return uid
    global curruser 
    curruser = uid

    print_mainmenu()

def print_createacc():
    print("----------------------------------------")
    # Multiple accounts under same email allowed
    email = input("Email: ")
    # Make sure that username is unique
    username = input("Username: ")

    cur = con.cursor()
    cur.execute("SELECT username FROM users")

    # gets an array of tuples
    users = [r[0] for r in cur.fetchall()]
    #print(users)

    if username in users:
        print("Username already exists.")
        print_createacc()

    password = input("Password: ")
    firstname = input("First name: ")
    lastname = input("Last name: ")

    print("Creating account...")

    # Get number of rows for uid
    SQL = "SELECT COUNT(*) FROM users"
    cur.execute(SQL)
    result = cur.fetchone()
    uid = result[0]

    # add user
    d = date.today()
    dt = datetime.now()
    SQL = "INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    data = (uid, email, username, password, firstname, lastname, d, dt)
    cur.execute(SQL, data)

    # create user's catalogue
    create_catalogue(uid, username)

    # save changes
    con.commit()
    cur.close()

    print("{} added to the database.".format(username))
    print_signin()

def create_catalogue(uid, username):
    print("Creating {}'s catalogue...".format(username))

    cur = con.cursor()

    # Make cid same as uid
    SQL = "INSERT INTO catalogue VALUES (%s, %s)"
    data = (uid, uid)
    cur.execute(SQL, data)

def print_mainmenu():
    print("----------------------------------------")
    print("1. Status")
    print("2. Add tool")
    print("3. Edit tool")
    print("4. Delete tool")
    print("5. Add category")
    print("6. Search for tool")
    print("9. Exit")

    val = input("Select: ")
    match int(val):
        case 1:
            return
        case 2:
            print_addtool()
        case 5:
            print_addcategory()
        case 9:
            print("Exiting...")
            exit()
        case default:
            print_mainmenu()

def print_addcategory():
    print("----------------------------------------")
    categoryname = input("Category name: ")

    cur = con.cursor()

    # Get number of rows
    SQL = "SELECT COUNT(*) FROM categories"
    cur.execute(SQL)
    result = cur.fetchone()
    rowcount = result[0]

    # Insert into category list table
    SQL = "INSERT INTO categories VALUES (%s, %s, %s)"
    data = (categoryname, rowcount, curruser)
    cur.execute(SQL, data)

    # Create new category itself
    

    print("Created {} category.".format(categoryname))

    # save changes
    con.commit()
    cur.close()

    print_mainmenu()

def print_categories():
    print("----------------------------------------")
    cur = con.cursor()

    # Select all user's categories
    SQL = "SELECT catid, category FROM categories WHERE uid = %s"
    data = (curruser,)
    cur.execute(SQL, data)

    results = cur.fetchall()

    catid = [r[0] for r in results]
    categoryname = [r[1] for r in results]

    for x, y in zip(catid, categoryname):
        print(x, y)

    print("----------------------------------------")

    cur.close()


def print_addtool():
    print("----------------------------------------")

    name = input("Name: ")
    description = input("Description: ")
    shareable = input("Shareable: ")
    price = input("Price: ")

    print_categories()

    print("Choose categories and separate by spaces. Eg: 0 1 2")
    categories = input("Categories: ")

    print("Creating tool...")

def exit():
    # save changes
    con.commit()

    # close the connection
    con.close()

    print("Exited.")

if __name__ == "__main__":
    main()
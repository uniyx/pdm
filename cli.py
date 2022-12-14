"""
cli.py, Command line interface for PDM Tools Database
Author: Gian Esteves
"""

from tools import *
import hashlib
from collections import Counter


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
    username = input("Enter Username or 'Back': ")
    if username == 'Back':
        print_signin()

    # Find if user exists
    cur = con.cursor()
    cur.execute("SELECT username FROM users")

    # gets an array of tuples
    users = [r[0] for r in cur.fetchall()]
    # print(users)

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
    # lastaccess = [r[2] for r in results][0]
    password = secure(password)
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
    email = input("To stop creating an account, enter 'Back', otherwise enter your Email: ")
    if email == 'Back':
        print_signin()
    # Make sure that username is unique
    username = input("Username: ")
    if username == 'Back':
        print("Invalid Username")
        print_createacc()

    cur = con.cursor()
    cur.execute("SELECT username FROM users")

    # gets an array of tuples
    users = [r[0] for r in cur.fetchall()]
    # print(users)

    if username in users:
        print("Username already exists.")
        print_createacc()

    password = input("Password: ")
    password = secure(password)
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
    print("When creating tools, Please create a category first")
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
    print("7. View catalogue")
    print("8. Manage requests")
    print("9. Sign out")
    print("10. Recommendations")
    print("11. Show your most borrowed and lent tools")
    print("0. Exit")

    val = input("Select: ")
    match int(val):
        case 1:
            print_status()
        case 2:
            print_addtool()
        case 3:
            print_tooledit()
        case 4:
            print_tooldelete()
        case 5:
            print_addcategory()
        case 7:
            print_catalogue()
            print_mainmenu()
        case 8:
            print_managerequests()
        case 9:
            print_login()
        case 10:
            recommend()
            print_mainmenu()
        case 11:
            mostBandL()
            print_mainmenu()
        case 0:
            exit()
        case default:
            print_mainmenu()


def print_addcategory():
    print("----------------------------------------")
    categoryname = input("Category name: or enter 'Back'")
    if categoryname == "Back":
        print_mainmenu()

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
    cur = con.cursor()

    # Get number of rows
    SQL = "SELECT barcode FROM tools ORDER BY barcode DESC"
    cur.execute(SQL)
    result = cur.fetchone()
    barcode = result[0] + 1

    name = input("Name: or enter 'Back'")
    if name == 'Back':
        print_mainmenu()
    description = input("Description: ")
    purchaseprice = input("Price (rounded to whole number): ")
    shareable = input("Shareable: ")

    print_categories()

    print("Choose categories and separate by spaces. Eg: 0 1 2")
    categories = input("Categories: ")
    purchasedate = datetime.now()

    # Insert into tools table
    SQL = "INSERT INTO tools VALUES (%s, %s, %s, %s, %s, %s, %s)"
    data = (barcode, name, description, purchaseprice, shareable, purchasedate, False)
    cur.execute(SQL, data)

    # Update tool_categories table
    catlist = categories.split()

    for catid in catlist:
        SQL = "INSERT INTO tool_categories VALUES (%s, %s)"
        data = (catid, barcode)
        cur.execute(SQL, data)

    # Update catalogue_tools table
    SQL = "INSERT INTO catalogue_tools VALUES (%s, %s)"
    data = (curruser, barcode)
    cur.execute(SQL, data)

    print("Created {} tool.".format(name))

    # save changes
    con.commit()
    cur.close()

    print_mainmenu()


def print_tools():
    print("----------------------------------------")
    cur = con.cursor()

    # Select all user's tool ids from catalogue_tools table
    SQL = "SELECT toolid FROM catalogue_tools WHERE clogid = %s ORDER BY toolid ASC"
    data = (curruser,)
    cur.execute(SQL, data)

    barcodes = [r[0] for r in cur.fetchall()]

    # Select all tools from tool table
    for barcode in barcodes:
        SQL = "SELECT * FROM tools WHERE barcode = %s"
        data = (barcode,)
        cur.execute(SQL, data)

        tool = [r for r in cur.fetchall()]
        tool = list(tool[0])

        SQL = "SELECT catid FROM tool_categories WHERE toolid = %s"
        data = (barcode,)
        cur.execute(SQL, data)

        categories = [r for r in cur.fetchall()]
        catnames = []

        for category in categories:
            catid = int(category[0])

            SQL = "SELECT category FROM categories WHERE catid = %s"
            data = (catid,)
            cur.execute(SQL, data)

            catnames.append(cur.fetchall()[0][0])

        print(
            "Barcode: {}, Name: {}, Description: {}, Price: {}, Date: {}, Categories: {}, Shareable: {}".format(tool[0],
                    tool[1], tool[2], tool[3], tool[5], catnames, tool[4]))

    cur.close()


def print_tooledit():
    print_tools()
    print("----------------------------------------")
    cur = con.cursor()

    print("Select a tool to edit")

    cur.execute("SELECT barcode FROM tools")
    codes = [r[0] for r in cur.fetchall()]
    loop = True
    barcode = input("Barcode: or enter 'Back'")
    while loop:
        if barcode == 'Back':
            cur.close()
            print_mainmenu()
        for r in codes:
            if ("%s" % r) == barcode:
                loop = False
                break
        if not loop:
            break
        barcode = input("INVALID BARCODE. Please enter valid barcode:")


    print("----------------------------------------")
    print("1. Name")
    print("2. Desciption")
    print("3. Purchase Price")
    print("4. Purchase Date")
    print("5. Categories")
    print("6. Shareable")

    val = input("Select attribute to edit: ")
    match int(val):
        case 1:
            newdata = input("New Name: ")

            SQL = "UPDATE tools SET name = %s WHERE barcode = %s"
            data = (newdata, barcode)
            cur.execute(SQL, data)
        case 2:
            newdata = input("New Description: ")

            SQL = "UPDATE tools SET description = %s WHERE barcode = %s"
            data = (newdata, barcode)
            cur.execute(SQL, data)
        case 3:
            newdata = input("New Purchase Price: ")

            SQL = "UPDATE tools SET purchaseprice = %s WHERE barcode = %s"
            data = (newdata, barcode)
            cur.execute(SQL, data)
        case 4:
            newdata = input("New Purchase Date: ")

            SQL = "UPDATE tools SET purchasedate = %s WHERE barcode = %s"
            data = (newdata, barcode)
            cur.execute(SQL, data)
        case 5:
            # Delete old categories
            SQL = "DELETE FROM tool_categories WHERE toolid = %s"
            data = (barcode,)
            cur.execute(SQL, data)

            print_categories()

            print("Choose categories and separate by spaces. Eg: 0 1 2")
            categories = input("Categories: ")

            # Update tool_categories table
            catlist = categories.split()

            for catid in catlist:
                SQL = "INSERT INTO tool_categories VALUES (%s, %s)"
                data = (catid, barcode)
                cur.execute(SQL, data)

        case 6:
            newdata = input("New Shareable, 0 or 1: ")

            SQL = "UPDATE tools SET shareable = %s WHERE barcode = %s"
            data = (newdata, barcode)
            cur.execute(SQL, data)
        case default:
            print_tooledit()

    cur.close()

    # save changes
    con.commit()
    cur.close()

    print_mainmenu()


def print_tooldelete():
    print_tools()
    print("----------------------------------------")
    cur = con.cursor()

    print("Select a tool to delete")

    cur.execute("SELECT barcode FROM tools")
    codes = [r[0] for r in cur.fetchall()]
    loop = True
    barcode = input("Barcode: or enter 'Back'")
    while loop:
        if barcode == 'Back':
            cur.close()
            print_mainmenu()
        for r in codes:
            if ("%s" % r) == barcode:
                loop = False
                break
        if not loop:
            break
        barcode = input("INVALID BARCODE. Please enter valid barcode:")

    # Delete old categories
    SQL = "DELETE FROM tool_categories WHERE toolid = %s"
    data = (barcode,)
    cur.execute(SQL, data)

    # Delete from catalogue_tools
    SQL = "DELETE FROM catalogue_tools WHERE toolid = %s"
    data = (barcode,)
    cur.execute(SQL, data)

    # Delete tool
    SQL = "DELETE FROM tools WHERE barcode = %s"
    data = (barcode,)
    cur.execute(SQL, data)

    # save changes
    con.commit()
    cur.close()

    print_mainmenu()


def print_catalogue():
    print("----------------------------------------")
    cur = con.cursor()

    # Only print tools that are set as shareable
    # Select all user's tool ids from catalogue_tools table
    SQL = "SELECT * FROM tools WHERE shareable = %s ORDER BY name ASC"
    data = (True,)
    cur.execute(SQL, data)

    tools = [r for r in cur.fetchall()]

    if len(tools) == 0:
        print("No tools available")

        print_mainmenu()

    for tool in tools:

        barcode = tool[0]

        SQL = "SELECT * FROM catalogue_tools WHERE toolid = %s"
        data = (barcode,)
        cur.execute(SQL, data)

        owner = [r for r in cur.fetchall()][0][0]

        # ignore if curruser owns tool
        if owner == curruser:
            continue

        SQL = "SELECT username FROM users WHERE uid = %s"
        data = (owner,)
        cur.execute(SQL, data)

        owner = [r for r in cur.fetchall()][0][0]

        print("Owner: {}, Barcode: {}, Name: {}, Description: {}, Price: {}, Date: {}".format(owner, tool[0],
                                                                                              tool[1], tool[2], tool[3],
                                                                                              tool[5]))

    cur.close()


def print_status():
    print("----------------------------------------")
    cur = con.cursor()

    SQL = "SELECT * FROM users WHERE uid = %s"
    data = (curruser,)
    cur.execute(SQL, data)

    userdata = cur.fetchall()[0]
    name = userdata[4] + " " + userdata[5]

    print("UserID: {}, Username: {}, Email: {}, Name: {}, User since: {}".format(userdata[0], userdata[2],
                                                                                 userdata[1], name, userdata[6]))

    print_tools()

    cur.close()

    print_mainmenu()


def print_managerequests():
    print("----------------------------------------")
    cur = con.cursor()

    # Get sent requests
    SQL = "SELECT COUNT(*) FROM requests WHERE requester = %s AND status = %s"
    data = (curruser, 1)
    cur.execute(SQL, data)

    sentcount = cur.fetchall()[0][0]

    # Get received requests
    SQL = "SELECT COUNT(*) FROM requests WHERE requestee = %s AND status = %s"
    data = (curruser, 0)
    cur.execute(SQL, data)

    receivedcount = cur.fetchall()[0][0]

    print("1. Create request")
    print("2. View sent requests ({} new)".format(sentcount))
    print("3. View received requests ({} new)".format(receivedcount))
    print("4. Main menu")

    val = input("Select: ")
    match int(val):
        case 1:
            print_createrequest()
        case 2:
            print_sentrequests()
        case 3:
            print_receivedrequests()
        case 4:
            print_mainmenu()
        case defualt:
            print_managerequests()

    cur.close()

    print_mainmenu()


def print_sentrequests():
    print("----------------------------------------")
    cur = con.cursor()

    SQL = "SELECT * FROM requests WHERE requester = %s"
    data = (curruser,)
    cur.execute(SQL, data)

    requests = cur.fetchall()

    for request in requests:
        # Get tool name
        SQL = "SELECT NAME FROM tools WHERE barcode = %s"
        data = (request[1],)
        cur.execute(SQL, data)

        toolname = cur.fetchall()[0][0]

        # Status
        if request[3] == 0:
            statustext = "Waiting"
        elif request[3] == 1:
            statustext = "Borrowing"
        else:
            statustext = "Returned"

        # Get owner's name
        SQL = "SELECT username FROM users WHERE uid = %s"
        data = (request[6],)
        cur.execute(SQL, data)

        requestee = cur.fetchall()[0][0]

        print(
            "Request ID: {}, Status: {}, Tool: {}, Requestee: {}, Date Required: {}, Return Date: {}".format(request[0],
                                                                                                             statustext,
                                                                                                             toolname,
                                                                                                             requestee,
                                                                                                             request[2],
                                                                                                             request[
                                                                                                                 4]))

    cur.execute("SELECT rid FROM requests")
    rids = [r[0] for r in cur.fetchall()]
    loop = True
    rid = input("Select a requet id: or 'Back'")
    while loop:
        if rid == 'Back':
            cur.close()
            print_mainmenu()
        for r in rids:
            if ("%s" % r) == rid:
                loop = False
                break
        if not loop:
            break
        rid = input("INVALID RID. Please enter valid RID:")

    # Get request data
    SQL = "SELECT * FROM requests WHERE rid = %s"
    data = (rid,)
    cur.execute(SQL, data)

    requestdata = [r for r in cur.fetchall()]

    print(requestdata)

    status = requestdata[0][3]
    requestee = requestdata[0][6]
    toolid = requestdata[0][1]

    # User's options for the request
    if status == 0:
        print_managerequests()

    if status == 1:
        print("1. Return")
        print("2. Back")

        val = input("Select: ")
        match int(val):
            case 1:
                # Update status
                SQL = "UPDATE requests SET status = %s WHERE rid = %s"
                data = (2, rid)
                cur.execute(SQL, data)

                # Change catalogues
                SQL = "UPDATE catalogue_tools SET clogid = %s WHERE toolid = %s"
                data = (requestee, toolid)
                cur.execute(SQL, data)

                # Update shareable
                SQL = "UPDATE tools SET shareable = %s"
                data = (True,)
                cur.execute(SQL, data)

                con.commit()

                print("Returned the tool")
                print_managerequests()
            case 2:
                print_managerequests()
            case default:
                print_managerequests()

    if status == 2:
        print_managerequests()


def print_receivedrequests():
    print("----------------------------------------")
    cur = con.cursor()

    SQL = "SELECT * FROM requests WHERE requestee = %s"
    data = (curruser,)
    cur.execute(SQL, data)

    requests = cur.fetchall()

    for request in requests:
        # Get tool name
        SQL = "SELECT NAME FROM tools WHERE barcode = %s"
        barcode = (request[1],)
        cur.execute(SQL, barcode)

        toolname = cur.fetchall()[0][0]

        # Status
        if request[3] == 0:
            statustext = "Waiting"
        elif request[3] == 1:
            statustext = "Borrowing"
        else:
            statustext = "Returned"

        # Get owner's name
        SQL = "SELECT username FROM users WHERE uid = %s"
        data = (request[5],)
        cur.execute(SQL, data)

        requester = cur.fetchall()[0][0]

        print(
            "Request ID: {}, Status: {}, Tool: {}, Requester: {}, Date Required: {}, Return Date: {}".format(request[0],
                                                                                                             statustext,
                                                                                                             toolname,
                                                                                                             requester,
                                                                                                             request[2],
                                                                                                             request[
                                                                                                                 4]))

    cur.execute("SELECT rid FROM requests")
    rids = [r[0] for r in cur.fetchall()]
    loop = True
    rid = input("Select a requet id: or 'Back'")
    while loop:
        if rid == 'Back':
            cur.close()
            print_mainmenu()
        for r in rids:
            if ("%s"%r) == rid:
                loop = False
                break
        if not loop:
            break
        rid = input("INVALID RID. Please enter valid RID:")

    # Get request data
    SQL = "SELECT * FROM requests WHERE rid = %s"
    data = (rid,)
    cur.execute(SQL, data)

    requestdata = [r for r in cur.fetchall()]

    print(requestdata)

    status = requestdata[0][3]
    requester = requestdata[0][5]
    toolid = requestdata[0][1]

    # User's options for the request
    if status == 0:
        print("1. Accept")
        print("2. Decline")
        print("3. Back")

        val = input("Select: ")
        match int(val):
            case 1:
                # Update status
                SQL = "UPDATE requests SET status = %s WHERE rid = %s"
                data = (1, rid)
                cur.execute(SQL, data)

                # Change catalogues
                SQL = "UPDATE catalogue_tools SET clogid = %s WHERE toolid = %s"
                data = (requester, toolid)
                cur.execute(SQL, data)

                # Update shareable
                SQL = "UPDATE tools SET shareable = %s"
                data = (False,)
                cur.execute(SQL, data)

                cur.execute("UPDATE tool_stats SET times_lent = times_lent + 1 WHERE barcode = %s", barcode)

                con.commit()

                print("Accepted the request")
                print_managerequests()
            case 2:
                SQL = "UPDATE requests SET status = %s WHERE rid = %s"
                data = (2, rid)
                cur.execute(SQL, data)

                con.commit()

                print("Declined the request")
                print_managerequests()
            case 3:
                print_managerequests()

    if status == 1:
        print_managerequests()

    if status == 2:
        print_managerequests()

    # save changes
    con.commit()
    cur.close()

    print_managerequests()


def print_createrequest():
    print("----------------------------------------")
    cur = con.cursor()

    print_catalogue()

    print("Choose which tool you would like to request")
    barcode = input("Select: or enter 'Back'")
    if barcode == "Back":
        print_mainmenu()
    print("What date would you want the tool by (2002-09-17)")
    date = input("Date: ")
    date = datetime.strptime(date, '%Y-%m-%d')
    print("What date will you return the tool by (2002-09-17)")
    returndate = input("Return Date: ")
    returndate = datetime.strptime(returndate, '%Y-%m-%d')

    # Get requested tool's owner
    SQL = "SELECT clogid FROM catalogue_tools WHERE toolid = %s"
    data = (barcode,)
    cur.execute(SQL, data)

    owner = cur.fetchall()[0][0]

    # Check if requests table empty
    SQL = "SELECT COUNT(*) FROM requests"
    cur.execute(SQL)

    rowcount = cur.fetchall()[0][0]
    if rowcount == 0:
        rid = 0
    else:
        # Get number of rows
        SQL = "SELECT rid FROM requests ORDER BY rid DESC"
        cur.execute(SQL)
        result = cur.fetchone()
        rid = result[0] + 1

    SQL = "INSERT INTO requests VALUES (%s, %s, %s, %s, %s, %s, %s)"
    data = (rid, barcode, date, 0, returndate, curruser, owner)
    cur.execute(SQL, data)

    # Get owner's name
    SQL = "SELECT username FROM users WHERE uid = %s"
    data = (owner,)
    cur.execute(SQL, data)

    ownername = cur.fetchall()[0][0]
    print("Made request to {}".format(ownername))

    # save changes
    con.commit()
    cur.close()
    print("\n")
    recommend()

    print_mainmenu()


def exit():
    # save changes
    con.commit()

    # close the connection
    con.close()

    return quit()


def secure(password):
    password = "popo9090" + password + "popo9090"
    secure_password = password.encode()
    hashed_pass = hashlib.sha3_512(secure_password)
    return hashed_pass.hexdigest()


def recommend():
    cur = con.cursor()
    cur.execute("SELECT barcode FROM tool_stats ORDER BY times_lent DESC")
    temp = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT barcode FROM tools WHERE shareable = true")
    shareable = [r[0] for r in cur.fetchall()]
    for r in temp:
        if r not in shareable:
            temp.remove(r)
    SQL = "SELECT name FROM tools where barcode = %s"
    data = (temp[0],)
    cur.execute(SQL, data)
    one = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT name FROM tools where barcode = %s", (temp[1],))
    two = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT name FROM tools where barcode = %s", (temp[2],))
    three = [r[0] for r in cur.fetchall()]
    print("We recommend checking out these popular tools:")
    print("Name: %s\t Barcode: %d" % (one[0], temp[0]))
    print("Name: %s\t Barcode: %d" % (two[0], temp[1]))
    print("Name: %s\t Barcode: %d" % (three[0], temp[2]))
    cur.close()


def mostBandL():
    cur = con.cursor()
    cur.execute("SELECT barcode FROM requests WHERE requester  = %s ORDER BY barcode DESC", (curruser,))
    barcodes = [r[0] for r in cur.fetchall()]
    barcode = Counter(barcodes)
    print("In order, your 10 most commonly borrowed tools are: ")
    p = 0
    length = len(barcode.most_common())
    while p < 10 and p < length:
        code = barcode.most_common(10)[p][0]
        cur.execute("SELECT name FROM tools WHERE barcode = %s", (code,))
        name = cur.fetchone()
        print("%s (%s)" %(name[0], code))
        p += 1
    cur.execute("SELECT barcode FROM requests WHERE requestee  = %s ORDER BY barcode DESC", (curruser,))
    barcodes = [r[0] for r in cur.fetchall()]
    barcode = Counter(barcodes)
    print("In order, your 10 most commonly lent tools are: ")
    p = 0
    length = len(barcode.most_common())
    while p < 10 and p < length:
        code = barcode.most_common(10)[p][0]
        cur.execute("SELECT name FROM tools WHERE barcode = %s", (code,))
        name = cur.fetchone()
        print("%s (%s)" % (name[0], code))
        p += 1
    cur.close()


if __name__ == "__main__":
    main()

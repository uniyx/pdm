from tools import *

def main():
    global con
    con = sshtunnel()
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
            print("cum 2")
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
    print(users)

    if username not in users:
        print("Could not find user")
        print_login()

    # Proceed if user exists
    password = input("Password: ")
    SQL = "SELECT password FROM users WHERE username = %s"
    data = (username,)
    cur.execute(SQL, data)
    realpassword = [r[0] for r in cur.fetchall()][0]

    print(realpassword)

    if password == realpassword:
        print("Successfully logged in as {}.".format(username))

    # close cursor
    cur.close()

def print_creatacc():
    print("test")


if __name__ == "__main__":
    main()
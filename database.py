#!/usr/bin/env python3

from modules import pg8000
import configparser


################################################################################
# Connect to the database
#   - This function reads the config file and tries to connect
#   - This is the main "connection" function used to set up our connection
################################################################################

def database_connect():
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create a connection to the database
    connection = None
    try:
        '''
        connect(database='y12i2120_unikey',
            host='soit-db-pro-2.ucc.usyd.edu.au,
            password='password_from_config',
            user='y19i2120_unikey')
        '''
        connection = pg8000.connect(database=config['DATABASE']['database'],
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    except Exception as e:
        print(e)

    # Return the connection to use
    return connection


################################################################################
# Login Function
#   - This function performs a "SELECT" from the database to check for the
#       student with the same unikey and password as given.
#   - Note: This is only an exercise, there's much better ways to do this
################################################################################

def check_login(sid, pwd):
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT *
                 FROM unidb.student
                 WHERE studid=%s AND password=%s"""
        cur.execute(sql, (sid, pwd))
        r = cur.fetchone()  # Fetch the first row
        cur.close()  # Close the cursor
        conn.close()  # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error Invalid Login")
    cur.close()  # Close the cursor
    conn.close()  # Close the connection to the db
    return None


# list all the academic staff function
def list_staff():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if (conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""
                        SELECT id, name, deptid, address
                        FROM unidb.academicstaff
                    """)
        val = cur.fetchall()
        return val
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")
        return None
    finally:
        cur.close()  # Close the cursor
        conn.close()  # Close the connection to the db


# search for staff in a particular department
def search_staff(first_name, last_name, department):
    # only enter first_name: .strip() + "%"
    name = (first_name.strip() + " " + last_name.strip()).lower().strip() + "%"

    conn = database_connect()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
                SELECT id, name, deptid
                FROM unidb.academicstaff 
                WHERE LOWER(name) LIKE %s
                AND deptid = %s 
            """
        cur.execute(sql, (name, department))
        r = cur.fetchone()  # Fetch the first row
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error: Invalid Input")
        return None
    finally:
        cur.close()  # Close the cursor
        conn.close()  # Close the connection to the db


# the number of staff in each department
def each_department():
    conn = database_connect()
    if conn is None:
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    try:
        cur.execute("""
                        SELECT deptid, COUNT(id)
                        FROM unidb.academicstaff 
                        GROUP BY deptid
                    """)
        val = cur.fetchall()
        return val
    except:
        # If there were any errors, we print something nice and return a NULL value
        print("Error fetching from database")
        return None
    finally:
        cur.close()  # Close the cursor
        conn.close()  # Close the connection to the db


# add a new academic staff
def add_staff(staff_id, name, deptid, password, address, salary):
    # invalid input handle
    if len(staff_id) != 9 or len(name) > 20 or len(deptid) != 3 or len(password) > 10 or len(address) > 50:
        print("Error: Invalid Input")
        return None
    try:
        salary = int(salary)
    except:
        print("Error: Invalid Input")
        return None

    conn = database_connect()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        sql = """
                INSERT INTO unidb.academicstaff(id, name, deptid, password, address, salary)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *;
            """
        cur.execute(sql, (staff_id, name, deptid, password, address, int(salary)))     # cur.execute() return None
        r = cur.fetchone()
        # insert successfully in this function but not successfully in the database... find out
        # commit the transaction!!!
        conn.commit()
        return r
    except:
        # If any errors
        conn.rollback()
        print("Error: Invalid Input")
        return None
    finally:    # finally: release resources, execute before return
        cur.close()  # Close the cursor
        conn.close()  # Close the connection to the db


def get_departments():
    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()
    try:
        cur.execute("""
                            SELECT DISTINCT deptid
                            FROM unidb.academicstaff
                        """)
        val = cur.fetchall()
        return val
    except:
        print("Error fetching from database")
        return None
    finally:
        cur.close()  # Close the cursor
        conn.close()  # Close the connection to the db


# find units the staff teaches
def find_units(first_name, last_name):
    # only enter first_name: .strip() + "%"
    name = (first_name.strip() + " " + last_name.strip()).lower().strip() + "%"

    conn = database_connect()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        sql = """
                SELECT DISTINCT S.uoscode, S.uosname
                FROM unidb.academicstaff A JOIN unidb.uosoffering U ON(A.id = U.instructorid)
                    JOIN unidb.unitofstudy S ON(U.uoscode = S.uoscode)
                WHERE LOWER(name) LIKE %s
            """
        cur.execute(sql, (name, ))
        r = cur.fetchall()  # Fetch the first row
        return r
    except:
        print("Error: Invalid Input")
        return None
    finally:
        cur.close()  # Close the cursor
        conn.close()  # Close the connection to the db


# find assessments of the unit
def find_assessments(uoscode):
    uoscode = uoscode.strip().upper()

    conn = database_connect()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        sql = """
                SELECT *
                FROM unidb.assessment
                WHERE uoscode = %s
            """
        cur.execute(sql, (uoscode, ))
        r = cur.fetchall()  # Fetch the first row
        return r
    except:
        print("Error: Invalid Input")
        return None
    finally:
        cur.close()  # Close the cursor
        conn.close()  # Close the connection to the db


#####################################################
#  Python code if you run it on it's own as 2tier
#####################################################
if __name__ == '__main__':
    print("{}\n{}\n{}".format("=" * 50, "Welcome to the 2-Tier Python Database", "=" * 50))
    print("""
This file is to interact directly with the database.
We're using the unidb (make sure it's in your database)

Try to execute some functions:
check_login('3070799133', 'random_password')
check_login('3070088592', 'Green')
list_units()""")

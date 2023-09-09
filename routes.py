# Importing the Flask Framework

from modules import *
from flask import *
import database
import configparser


page = {}
session = {}

# Initialise the FLASK application
app = Flask(__name__)
app.secret_key = 'SoMeSeCrEtKeYhErE'


# Debug = true if you want debug output on error ; change to false if you dont
app.debug = True


# Read my unikey to show me a personalised app
config = configparser.ConfigParser()
config.read('config.ini')
unikey = config['DATABASE']['user']
portchoice = config['FLASK']['port']

#####################################################
##  INDEX
#####################################################

# What happens when we go to our website
@app.route('/')
def index():
    # If the user is not logged in, then make them go to the login page
    if( 'logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    page['unikey'] = unikey
    page['title'] = 'Welcome'
    return render_template('welcome.html', session=session, page=page)

################################################################################
# Login Page
################################################################################

# This is for the login
# Look at the methods [post, get] that corresponds with form actions etc.
@app.route('/login', methods=['POST', 'GET'])
def login():
    page = {'title' : 'Login', 'unikey' : unikey}
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get our login value
        val = database.check_login(request.form['sid'], request.form['password'])

        # If our database connection gave back an error
        if(val == None):
            flash("""Error with the database connection. Please check your terminal
            and make sure you updated your INI files.""")
            return redirect(url_for('login'))

        # If it's null, or nothing came up, flash a message saying error
        # And make them go back to the login screen
        if(val is None or len(val) < 1):
            flash('There was an error logging you in')
            return redirect(url_for('login'))
        # If it was successful, then we can log them in :)
        session['name'] = val[1]
        session['sid'] = request.form['sid']
        session['logged_in'] = True
        return redirect(url_for('index'))
    else:
        # Else, they're just looking at the page :)
        if('logged_in' in session and session['logged_in'] == True):
            return redirect(url_for('index'))
        return render_template('index.html', page=page)


################################################################################
# Logout Endpoint
################################################################################

@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You have been logged out')
    return redirect(url_for('index'))


# list all the academic staff Page
@app.route('/list_staff')
def list_staff():
    staff = database.list_staff()
    if staff is None:
        # Set it to an empty list and show error message
        staff = []
        flash('Error, there is no staff')
    # page=page, session=session because every html includes top.html which needs it
    return render_template('list_staff.html', page=page, session=session, staff=staff)


# search for a staff
@app.route('/search_staff', methods=['POST', 'GET'])
def search_staff():
    # for drop down list
    departments = database.get_departments()

    if request.method == 'POST':
        # Get the name of the staff
        staff = database.search_staff(request.form['first_name'], request.form['last_name'], request.form['department'])

        # If it's null, or nothing came up, flash a message saying error
        if staff is None or len(staff) < 1:
            flash('Not Found')
            # {% with messages = get_flashed_messages() %} in top.html
            return redirect(url_for('search_staff'))

        # If successful,
        return render_template('search_staff.html', page=page, session=session, departments=departments, staff=staff)

    else:
        # Else, they're just looking at the page :)
        return render_template('search_staff.html', page=page, session=session, departments=departments)


# list the number of staff in each department
@app.route('/each_department')
def each_department():
    result = database.each_department()

    # What happens if units are null?
    if result is None:
        # Set it to an empty list and show error message
        result = []
        flash('Error, there is no department')
    return render_template('each_department.html', page=page, session=session, result=result)


# add a new academic staff
@app.route('/add_staff', methods=['POST', 'GET'])
def add_staff():
    # If it's a post method handle it nicely
    if request.method == 'POST':
        # Get the information of the staff
        staff = database.add_staff(request.form['id'], request.form['name'], request.form['deptid'], request.form['password'], request.form['address'], request.form['salary'])

        # If got back error
        if staff is None:
            flash('Invalid Input')
            return redirect(url_for('add_staff'))

        # If successful
        return render_template('add_staff.html', page=page, session=session, staff=staff)

    else:
        # Else, they're just looking at the page :)
        return render_template('add_staff.html', page=page, session=session)


# find units the staff teaches
@app.route('/find_units', methods=['POST', 'GET'])
def find_units():
    if request.method == 'POST':
        units = database.find_units(request.form['first_name'], request.form['last_name'])
        # If got back error or result is empty
        if units is None or len(units) < 1:
            flash('Not Found')
            return redirect(url_for('find_units'))
        # If successful
        return render_template('find_units.html', page=page, session=session, units=units)
    else:
        # Else, they're just looking at the page :)
        return render_template('find_units.html', page=page, session=session)


# find assessments of the unit
@app.route('/find_assessments', methods=['POST', 'GET'])
def find_assessments():
    if request.method == 'POST':
        assessments = database.find_assessments(request.form['uoscode'])
        # If got back error or result is empty
        if assessments is None or len(assessments) < 1:
            flash('Not Found')
            return redirect(url_for('find_assessments'))
        # If successful
        return render_template('find_assessments.html', page=page, session=session, assessments=assessments)
    else:
        # Else, they're just looking at the page :)
        return render_template('find_assessments.html', page=page, session=session)


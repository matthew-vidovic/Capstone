import RPi.GPIO as GPIO    
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import serial
from time import sleep

#import bluetooth
ser = serial.Serial('/dev/rfcomm0',9600)


app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
led = 13

GPIO.setup(led,GPIO.OUT)
GPIO.output(led,GPIO.LOW)
ledSts = GPIO.input(led)

#rgb
rgbred = 22
rgbgreen = 27
rgbblue = 17
GPIO.setup(rgbred,GPIO.OUT)
GPIO.setup(rgbgreen,GPIO.OUT)
GPIO.setup(rgbblue,GPIO.OUT)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'coyotes61'
app.config['MYSQL_DB'] = 'pythonlogin'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        #GPIO.output(13,GPIO.LOW)
        templateData = {
            'username':session['username'],
            'led':ledSts
            }
        return render_template('home.html', **templateData)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))



# @app.route('/home/led/<state>',methods=['GET','POST'])
# def ledControl(state):
#     if 'loggedin' in session:
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         templateData = {
#             'username':session['username'],
#             'led':ledSts
#             }
#         if state == 'true':
#             #prevValue = GPIO.input(led)
#             #GPIO.output(13,GPIO.HIGH)
#             ser.write(str.encode('1'))

#         else:
            
#             # prevValue = GPIO.input(led)
#             # GPIO.output(13,GPIO.LOW)
#             ser.write(str.encode('0'))
#             # templateData = {
#             #     'username':session['username'],
#             #     "led":ledSts
#             # }    

#         return render_template('home.html',**templateData)

#     return redirect(url_for('login'))

    
@app.route('/home/led',methods=['GET','POST'])
def ledControl():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        templateData = {
            'username':session['username'],
            'led':ledSts
            }
        if request.method == "POST":    
            state = request.get_data()
            print(state)
            if state.decode() == 'true':
                print('writing')
                #prevValue = GPIO.input(led)
                #GPIO.output(13,GPIO.HIGH)
                ser.write(str.encode('1'))
                
            else:
                
                # prevValue = GPIO.input(led)
                # GPIO.output(13,GPIO.LOW)
                ser.write(str.encode('3'))
                # templateData = {
                #     'username':session['username'],
                #     "led":ledSts
                # }    

        return render_template('home.html',**templateData)

    return redirect(url_for('login'))


    #lighting without rgb
# @app.route('/pythonlogin/home/led/<room>/true')
# def ledOn(room):
#     if 'loggedin' in session:
        
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
#         prevValue = GPIO.input(led)
#         GPIO.output(13,GPIO.HIGH)
#         ledSts = GPIO.input(led)
        
#         if(prevValue != 1):
#             cursor.execute('INSERT INTO lightUsage VALUES (NULL, %s, %s, NULL)', (session['id'], 1))
#             mysql.connection.commit() 
        
#         templateData = {
#             'username':session['username'],
#             "led":ledSts
#             }
#         return render_template('home.html',**templateData)

            
#     return redirect(url_for('login'))
    
        
@app.route('/home/rgb/<color>')
def rgbControl(color):
    if color == "red":
        GPIO.output(rgbred,GPIO.HIGH)
        GPIO.output(rgbgreen,GPIO.LOW)
        GPIO.output(rgbblue,GPIO.LOW)   
    elif color == "green":
        GPIO.output(rgbred,GPIO.LOW)
        GPIO.output(rgbgreen,GPIO.HIGH)
        GPIO.output(rgbblue,GPIO.LOW)   
    elif color == "blue": 
        GPIO.output(rgbred,GPIO.LOW)
        GPIO.output(rgbgreen,GPIO.LOW)
        GPIO.output(rgbblue,GPIO.HIGH)   
    elif color == 'white':
        GPIO.output(rgbred,GPIO.HIGH)
        GPIO.output(rgbgreen,GPIO.HIGH)
        GPIO.output(rgbblue,GPIO.HIGH)   
    elif color == 'yellow':
        GPIO.output(rgbred,GPIO.HIGH)
        GPIO.output(rgbgreen,GPIO.HIGH)
        GPIO.output(rgbblue,GPIO.LOW)   
    elif color == 'purple':
        GPIO.output(rgbred,GPIO.HIGH)
        GPIO.output(rgbgreen,GPIO.LOW)
        GPIO.output(rgbblue,GPIO.HIGH)   
    elif color == 'cyan':   
        GPIO.output(rgbred,GPIO.LOW)
        GPIO.output(rgbgreen,GPIO.HIGH)
        GPIO.output(rgbblue,GPIO.HIGH)   
    elif color == 'rainbow':
        while True:
            GPIO.output(rgbred,GPIO.HIGH)
            GPIO.output(rgbgreen,GPIO.LOW)
            GPIO.output(rgbblue,GPIO.LOW)
            sleep(1)

            #orange
            #yellow
            GPIO.output(rgbred,GPIO.HIGH)
            GPIO.output(rgbgreen,GPIO.HIGH)
            GPIO.output(rgbblue,GPIO.LOW) 
            sleep(1)

            #green
            GPIO.output(rgbred,GPIO.LOW)
            GPIO.output(rgbgreen,GPIO.HIGH)
            GPIO.output(rgbblue,GPIO.LOW) 
            sleep(1)
            #blue
            GPIO.output(rgbred,GPIO.LOW)
            GPIO.output(rgbgreen,GPIO.LOW)
            GPIO.output(rgbblue,GPIO.HIGH)  
            sleep(1)
            #indigo
            GPIO.output(rgbred,GPIO.LOW)
            GPIO.output(rgbgreen,GPIO.HIGH)
            GPIO.output(rgbblue,GPIO.HIGH)  
            sleep(1)

            #purple
            GPIO.output(rgbred,GPIO.HIGH)
            GPIO.output(rgbgreen,GPIO.LOW)
            GPIO.output(rgbblue,GPIO.HIGH) 
            sleep(1)
        else:   
            GPIO.output(rgbred,GPIO.LOW)
            GPIO.output(rgbgreen,GPIO.LOW)
            GPIO.output(rgbblue,GPIO.LOW) 
    return render_template('home.html')       

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM lightUsage WHERE user_id = %s', (session['id'],))
        lightUsage = cursor.fetchall()
        templateData = {
            "account":account,
            "lightUsage":lightUsage
            }
        # Show the profile page with account info
        return render_template('profile.html', **templateData)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run('192.168.100.186',port=5000,debug=True)
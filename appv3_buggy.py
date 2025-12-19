from flask import Flask, render_template, request, redirect, url_for, session, flash
from cryptography.fernet import Fernet
import os
import mysql.connector
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyotp
import time
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="p225_pwdmngr"
)

# Simulating a simple in-memory storage for OTP (For production use, use a database)
otp_store = {}

# OTP Expiry time (in seconds)
OTP_EXPIRY = 300  # 5 minutes

cursor = db.cursor()

# Generate a key (only once, and store it securely)
def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

# Load the key from the key file
def load_key():
    if not os.path.exists("key.key"):
        generate_key()
    with open("key.key", "rb") as key_file:
        return key_file.read()

key = load_key()

# Encrypt a password
def encrypt_password(password):
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

# Decrypt a password
def decrypt_password(encrypted_password):
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()

# OTP Verification Route
@app.route('/send_otp', methods=['GET', 'POST'])
def send_otp():
    if 'username' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']
    email = users[username]["email"]

    # Generate OTP and send it to email
    otp = pyotp.HOTP(str(random.randint(1000, 9999)))  # You can use a more secure OTP generation here
    otp_code = otp.now()

    otp_store[user_id] = {'otp': otp_code, 'timestamp': time.time()}

    # Send OTP email
    msg = Message('Your OTP Code', recipients=[email])
    msg.body = f'Your OTP code is: {otp_code}'
    try:
        mail.send(msg)
        flash('OTP sent to your email.')
        return redirect(url_for('verify_otp'))
    except Exception as e:
        flash(f"Error sending email: {str(e)}")
        return redirect(url_for('send_otp'))

# OTP Verification Route
@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        user_id = session['user_id']
        entered_otp = request.form['otp']

        # Check OTP validity
        otp_details = otp_store.get(user_id)
        if otp_details:
            stored_otp = otp_details['otp']
            timestamp = otp_details['timestamp']
            
            # Check if OTP is expired
            if time.time() - timestamp > OTP_EXPIRY:
                flash("OTP expired, please request a new one.")
                del otp_store[user_id]
                return redirect(url_for('send_otp'))
            
            # Verify OTP
            if entered_otp == stored_otp:
                flash('Login successful!')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid OTP. Please try again.')

        return redirect(url_for('verify_otp'))
    
    return render_template('verify_otp.html')


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = encrypt_password(request.form['password'])

        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, password))
        db.commit()
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and decrypt_password(user[1]) == password:
            session['user_id'] = user[0]
            return redirect(url_for('send_otp'))
            #return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    cursor.execute("SELECT service, username, password FROM passwords WHERE user_id = %s", (session['user_id'],))
    passwords = cursor.fetchall()

    decrypted_passwords = [(service, username, decrypt_password(password)) for service, username, password in passwords]
    return render_template('dashboard.html', passwords=decrypted_passwords)

@app.route('/add', methods=['POST'])
def add_password():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    service = request.form['service']
    username = request.form['username']
    password = encrypt_password(request.form['password'])

    cursor.execute("INSERT INTO passwords (user_id, service, username, password) VALUES (%s, %s, %s, %s)",
                   (session['user_id'], service, username, password))
    db.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

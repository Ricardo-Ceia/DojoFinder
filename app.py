from flask import Flask, jsonify, request,render_template,redirect,url_for,send_from_directory,session
from flask_mail import Mail,Message
from urllib.parse import urlencode, quote
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import sqlite3
from cachetools import cached, TTLCache
from threading import Thread
import numpy as np 
import os
import bcrypt


app = Flask(__name__)

app.secret_key = 'secret_key_benfica4895_glorioso'

locator = Nominatim(user_agent="meGeocoder")

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dojofinderinfo@gmail.com'  # Replace with your Gmail address
app.config['MAIL_PASSWORD'] = 'apzg wucx yhsr kqto'  # Replace with your App Password
app.config['MAIL_DEFAULT_SENDER'] = 'dojofinderinfo@gmail.com'  # Default sender email

mail = Mail(app)

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {str(e)}")


def send_dojo_data_email(app,dojo, schedules):
    # Format dojo information
    dojo_info = f"""
    New Dojo Listing:
    User ID: {dojo['user_id']}
    User Name: {dojo['username']}
    Name: {dojo['name']}
    Address: {dojo['address']}
    City: {dojo['city']}
    Website: {dojo['website']}
    Email: {dojo['email']}
    Phone: {dojo['phone']}
    Price per month: {dojo['price']}
    latitude: {dojo['latitude']}
    longitude: {dojo['longitude']}
    """
    
    # Format schedule information
    schedule_info = "\nSchedules:\n"
    for schedule in schedules:
        schedule_info += f"""
        - Day: {schedule['day_of_week']}
          Time: {schedule['start_time']} - {schedule['end_time']}
          Instructor: {schedule['instructor']}
          Competition Only: {schedule['competition_only']}
          Age Range: {schedule['age_range']}
        """

    # Combine all information
    email_body = dojo_info + schedule_info

    # Create and send the email
    msg = Message(
        subject="New Dojo Listing",
        recipients=["dojofinderinfo@gmail.com"],
        body=email_body
    )
    Thread(target=send_async_email, args=(app, msg)).start()
     

cache = TTLCache(maxsize=128, ttl=43200)  #12 hours of cache 

@cached(cache)
def get_coordinates(address):
    try:
        location = locator.geocode(address)
        if location:
            return (location.latitude,location.longitude)
    except Exception as e:
        print(f"Geocoding error for {address}: {str(e)}")
    return (None,None)


def get_dojo_details_with_schedules(dojo_id): 
    conn = sqlite3.connect('./DB/dojo_listings.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT d.name, d.address, d.website, d.email, d.sensei_path, d.image_path, d.phone, d.head_instructor,
               s.day_of_week, s.start_time, s.end_time, s.instructor, s.competition_only, s.age_range
        FROM dojos d
        LEFT JOIN schedules s ON d.id = s.dojo_id
        WHERE d.id = ?
    ''', (dojo_id,))
    
    results = cursor.fetchall()
    conn.close()

    # Process `results` into a dojo details object and a list of schedules
    if results:
        dojo_details = results[0][:8]  # First 9 fields are dojo details
        schedules = [result[8:] for result in results if result[8] is not None]  # Remaining fields are schedules
        return dojo_details, schedules
    else:
        return None, []

# Function to query the database
def get_dojos_by_city(city):

    conn = sqlite3.connect('./DB/dojo_listings.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT name, address, website, email, image_path, price_per_month,phone,id FROM dojos WHERE city LIKE ?""", ('%' + city.strip() + '%',))
    dojos = cursor.fetchall()
    conn.close()
    
    return dojos

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/get_dojos', methods=['POST'])
def get_dojos():
    city = request.form['location']

    dojos = get_dojos_by_city(city)

    if not dojos:
        return jsonify({'error': f'No dojos found in {city.strip()}'}),404
    
    # Render a partial template containing just the dojo list
    return render_template('dojo_list.html',dojos=dojos),200

@app.route('/premium_dojo_form',methods=['GET'])
def premiun_dojo_form():
    return render_template('premium_dojo_form.html'),200


@app.route('/dojo_details',methods=['GET'])
def dojo_details():
    dojo_id = request.args.get('dojo_id')

    dojo_details,schedules = get_dojo_details_with_schedules(dojo_id)

    return render_template('dojo_details.html',dojo_details=dojo_details,schedules=schedules)

@app.route('/add_dojo_to_premium', methods=['POST'])
def add_dojo_to_premium():
    if 'user_id' not in session:
        redirect('/login'),401
    user_id = session['user_id']
    name = request.form.get('dojo_name')
    address = request.form.get('address')
    city = request.form.get('city')
    website = request.form.get('website') or None
    email = request.form.get('email')
    phone = request.form.get('phone')
    price = request.form.get('class_price') 
    head_instructor = request.form.get('head_instructor')

    #Get the location coords of the dojo
    latitude, longitude = get_coordinates(address)
    # Get the image files
    dojo_image = request.files.get('dojo_image')
    sensei_image = request.files.get('sensei_image')
    #get the schedule data
    index=0
    schedule_entries = []

    while True:
        day_of_week = request.form.get(f'schedules[{index}][day_of_week]')
        start_time = request.form.get(f'schedules[{index}][start_time]')
        end_time = request.form.get(f'schedules[{index}][end_time]')
        instructor = request.form.get(f'schedules[{index}][instructor]')
        competition_only = request.form.get(f'schedules[{index}][competition_only]') == "on"
        age_range = request.form.get(f'schedules[{index}][age_range]')
        
        if not day_of_week or not start_time or not end_time or not instructor or not age_range:
            break

        schedule_entries.append({
            'day_of_week': day_of_week,
            'start_time': start_time,
            'end_time': end_time,
            'instructor': instructor,
            'competition_only': competition_only,
            'age_range': age_range
        })

        index += 1

    # Check if main dojo image exists
    if dojo_image:
        # Save dojo image
        dojo_image_path = os.path.join(app.config['UPLOAD_FOLDER'], dojo_image.filename)
        dojo_image.save(dojo_image_path)

        # Save sensei image if provided
        sensei_image_path = None
        if sensei_image:
            sensei_image_path = os.path.join(app.config['UPLOAD_FOLDER'], sensei_image.filename)
            sensei_image.save(sensei_image_path)

        # Database connection
        conn = sqlite3.connect('./DB/dojo_listings.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO dojos (
                user_id,name,address,city,website,phone,email,sensei_path,image_path,price_per_month,head_instructor,latitude,longitude
            )
            VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
        ''', (
            user_id,name, address, city,website,
            phone, email, sensei_image_path,dojo_image_path,price,head_instructor,latitude,longitude
        ))
        conn.commit()

        #get the id of the dojo
        dojo_id = cursor.lastrowid
            
        for schedule_entry in schedule_entries:
            cursor.execute("""
            INSERT INTO schedules (
                dojo_id, day_of_week, start_time, end_time, instructor, competition_only,age_range
            ) VALUES (?, ?, ?, ?, ?, ?,?)
        """, (
            dojo_id,
            schedule_entry['day_of_week'],
            schedule_entry['start_time'],
            schedule_entry['end_time'],
            schedule_entry['instructor'],
            schedule_entry['competition_only'],
            schedule_entry['age_range']
            ))
        conn.commit()
        conn.close()

        dojo = {
            'user_id': user_id,
            'username': session['username'],
            'name': name,
            'address': address,
            'city': city,
            'website': website,
            'email': email,
            'phone': phone,
            'price': price,
            'head_instructor': head_instructor,
            'latitude': latitude,
            'longitude': longitude
        }

        send_dojo_data_email(app,dojo, schedule_entries)

        return redirect('/')
    
@app.route('/get_near_me',methods=['POST'])
def get_near_me():
    #location of the user
    user_latitude = float(request.form.get('latitude'))
    user_longitude = float(request.form.get('longitude'))

    conn = sqlite3.connect('./DB/dojo_listings.db')
    cursor = conn.cursor()
    
    # Optimize query by adding spatial bounds
    # This creates a bounding box around the user's location
    # 1 degree of latitude ≈ 69 miles, so 0.15 degrees ≈ 10 miles
    lat_range = 0.15
    lon_range = 0.15 / np.cos(np.radians(user_latitude))  # Adjust for longitude distance variation

    cursor.execute('''
        SELECT id, latitude, longitude 
        FROM dojos 
        WHERE latitude BETWEEN ? AND ?
        AND longitude BETWEEN ? AND ?
    ''', (
        user_latitude - lat_range, user_latitude + lat_range,
        user_longitude - lon_range, user_longitude + lon_range
    ))
    
    potential_dojos = cursor.fetchall()

    dojos_near_user = []

    for dojo in potential_dojos:
        dojo_coords = (dojo[1],dojo[2])
        user_coords = (user_latitude,user_longitude)
        dojo_distance = geodesic(user_coords,dojo_coords).miles
        if dojo_distance < 10:
            cursor.execute("""SELECT name, address, website, email, image_path, price_per_month,phone,id 
                           FROM dojos WHERE id LIKE ?""",
                            ('%' + str(dojo[0]) + '%',))
            dojo = cursor.fetchone()
            
            if not dojo:
                return jsonify({'error':'No dojos found near you!'}),404
        
            dojos_near_user.append(dojo)

    conn.close()

    return render_template('dojo_list.html',dojos=dojos_near_user)

@app.route('/signup',methods=['GET'])
def signup():
    return render_template('signup.html'),200

@app.route('/login',methods=['GET'])
def login():
    return render_template('login.html'),200

@app.route('/signup_form',methods=['POST'])
def signup_form():
    username = request.form.get('username').strip()
    email = request.form.get('email').strip()
    password = request.form.get('password').strip()
    confirm_password = request.form.get('confirm_password').strip()
    if not username or not email or not password or not confirm_password:
        return jsonify({'error':'username, email, password and confirm password are required!'}),400
    if password != confirm_password:
        return jsonify({'error':'password and confirm password do not match!'}),400
    
    try:
        password_hash = bcrypt.hashpw(password.encode(),bcrypt.gensalt())
        conn = sqlite3.connect('./DB/dojo_listings.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? OR username = ?',(email,username))
        if cursor.fetchone():
            return 
        cursor.execute('''
            INSERT INTO users (username,email,password) VALUES (?,?,?)
        ''',(username,email,password_hash))
        conn.commit()
        conn.close()
        return redirect('/login'),302
    except sqlite3.Error as e:
        print("Internal server error: ",str(e)) 
        return jsonify({'error':'Internal Server Error'}),500
    
@app.route('/login_form',methods=['POST'])
def login_form():
    email_or_username = request.form.get('email_or_username')
    password = request.form.get('password')
    if not email_or_username or not password:
        return jsonify({'error':'email/username and password are required!'}),400
    try:
        conn = sqlite3.connect('./DB/dojo_listings.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? OR username = ?',(email_or_username,email_or_username))
        user = cursor.fetchone()
        conn.close()
        if not user:
            return jsonify({"error":"username or password is incorrect!"}),404
        if not bcrypt.checkpw(password.encode(),user[3]):
            return jsonify({"error":"username or password is incorrect!"}),404
        
        session['user_id'] = user[0]
        session['username'] = user[1]
        return redirect('/premium_dojo_form'),302
    except sqlite3.Error as e:
        return jsonify({'error':str(e)}),500

        
         
@app.route('/')
def home():
    return render_template('./homePage.html')

if __name__ == '__main__':
    app.run(debug=True)

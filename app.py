from flask import Flask, jsonify, request,render_template,redirect,url_for,send_from_directory,session
from flask_mail import Mail,Message
from urllib.parse import urlencode, quote
import sqlite3
import os


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dojofinderinfo@gmail.com'  # Replace with your Gmail address
app.config['MAIL_PASSWORD'] = 'apzg wucx yhsr kqto'  # Replace with your App Password
app.config['MAIL_DEFAULT_SENDER'] = 'dojofinderinfo@gmail.com'  # Default sender email

mail = Mail(app)

def send_dojo_data_email(dojo, schedules):
    # Format dojo information
    dojo_info = f"""
    New Dojo Listing:
    Name: {dojo['name']}
    Address: {dojo['address']}
    City: {dojo['city']}
    Website: {dojo['website']}
    Email: {dojo['email']}
    Phone: {dojo['phone']}
    Price per month: {dojo['price']}
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
    mail.send(msg)
     

#function to query the database to get the dojo details by their id
def get_dojo_by_id(dojo_id):
    conn = sqlite3.connect('./DB/dojo_listings.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT name, address, website, email, sensei_path, athletes_path,image_path, phone,price_per_month FROM dojos WHERE id = ?''', (dojo_id,))
    dojo = cursor.fetchone()

    conn.close()

    return dojo

#function to query the databse to get the schedules by dojo_id
def get_schedules_by_dojo_id(dojo_id):
    conn = sqlite3.connect('./DB/dojo_listings.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT day_of_week, start_time, end_time, instructor, competition_only, age_range FROM schedules WHERE dojo_id = ?''', (dojo_id,))
    schedules = cursor.fetchall()

    conn.close()

    return schedules

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
    
    # Render a partial template containing just the dojo list
    return render_template('dojo_list.html',dojos=dojos)   


@app.route('/premium_dojo_form',methods=['GET'])
def premiun_dojo_form():
    return render_template('premium_dojo_form.html')


@app.route('/dojo_details',methods=['GET'])
def dojo_details():
    dojo_id = request.args.get('dojo_id')
    print(f"dojo_id:{dojo_id}")
    schedules = get_schedules_by_dojo_id(dojo_id)
    dojo_details = get_dojo_by_id(dojo_id)
    print(f"schedules:{schedules}")
    print(f"dojo_details:{dojo_details}")

    return render_template('dojo_details.html',dojo_details=dojo_details,schedules=schedules)

@app.route('/add_dojo_to_premium', methods=['POST'])
def add_dojo_to_premium():
    name = request.form.get('dojo_name')
    address = request.form.get('address')
    city = request.form.get('city')
    website = request.form.get('website') or None
    email = request.form.get('email')
    phone = request.form.get('phone')
    price = request.form.get('class_price') 
    # Get the image files
    dojo_image = request.files.get('dojo_image')
    sensei_image = request.files.get('sensei_image')
    athletes_image = request.files.get('athletes_image')
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

        # Save athletes image if provided
        athletes_image_path = None
        if athletes_image:
            athletes_image_path = os.path.join(app.config['UPLOAD_FOLDER'], athletes_image.filename)
            athletes_image.save(athletes_image_path)

        # Database connection
        conn = sqlite3.connect('./DB/dojo_listings.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO dojos (
                name,address,city,website,phone,email,sensei_path,athletes_path,image_path,price_per_month
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, address, city,website,
            phone, email, sensei_image_path, athletes_image_path,dojo_image_path,price
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
            'name': name,
            'address': address,
            'city': city,
            'website': website,
            'email': email,
            'phone': phone,
            'price': price
        }

        send_dojo_data_email(dojo, schedule_entries)

        return redirect('/')

@app.route('/')
def home():
    return render_template('./homePage.html')


    
if __name__ == '__main__':
    app.run(debug=True)

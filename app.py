from flask import Flask, jsonify, request,render_template,redirect,url_for,send_from_directory,session
from flask_mail import Mail,Message
from urllib.parse import urlencode, quote
import sqlite3
import stripe 
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

# Function to query the database
def get_dojos_by_city(city):
    print("This is the city recived by get_dojos_by_city:",city)
    conn = sqlite3.connect('./DB/dojo_listings.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT name, address, age_range FROM normal_listings WHERE city LIKE ?""", ('%' + city.strip() + '%',))
    normal = cursor.fetchall()

    cursor.execute("""SELECT name, address, age_range, sensei, athletes, email, phone, image_path, website FROM premium_listings WHERE city LIKE ?""", ('%' + city.strip() + '%',))
    premium_dojos = cursor.fetchall()
    conn.close()

    dojos={
        'normal':normal,
        'premium':premium_dojos
    }
    
    return dojos

@app.route('/get_dojos', methods=['POST'])
def get_dojos():
    city = request.form['location']
    
    dojos = get_dojos_by_city(city)
    
    # Render a partial template containing just the dojo list
    return render_template('dojo_list.html',normal_dojos=dojos['normal'], premium_dojos=dojos['premium'])   


@app.route('/paywall')
def paywall():
    return render_template('./paywall.html')

@app.route('/add_dojo')
def add_dojo():
    print("This is the add_dojo function!")
    return render_template('./add_dojo_form.html')

@app.route('/premium_dojo_form',methods=['GET'])
def premiun_dojo_form():
    return render_template('premium_dojo_form.html')

@app.route('/add_dojo_to_premium', methods=['POST'])
def add_dojo_to_premium():
    name = request.form.get('dojo_name')
    address = request.form.get('address')
    city = request.form.get('city')
    age_range = request.form.get('age_range')
    website = request.form.get('website') or None
    print(f"This is the website:{website}")
    email = request.form.get('email')
    phone = request.form.get('phone')

    # Get the image files
    dojo_image = request.files.get('dojo_image')
    sensei_image = request.files.get('sensei_image')
    athletes_image = request.files.get('athletes_image')

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
            INSERT INTO premium_listings (
                name,address,city,age_range,website,phone,email,Image_path,sensei,Athletes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, address, city, age_range, website,
            phone, email,dojo_image_path, sensei_image_path, athletes_image_path
        ))

        conn.commit()
        conn.close()

        return "Dojo successfully added to database", 200
    else:
        return "Dojo image upload failed", 400
    



@app.route('/confirm_dojo')
def confirm_dojo():
    # Use request.args.get() for URL parameters
    dojo_name = request.args.get('dojo_name')
    address = request.args.get('address')
    city = request.args.get('city')
    age_range = request.args.get('age_range')
    
    print(f"URL DATA: {dojo_name}, {address}, {city}, {age_range}")
    
    # Add error checking to ensure all parameters are present
    if not all([dojo_name, address, city, age_range]):
        return "Missing required parameters", 400
    
    try:
        conn = sqlite3.connect('./DB/dojo_listings.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO normal_listings (name, address, city, age_range)
            VALUES (?, ?, ?, ?)
        ''', (dojo_name, address, city, age_range))

        conn.commit()
        conn.close()
        
        return "Dojo successfully added to database", 200
        
    except Exception as e:
        if conn:
            conn.close()
        return f"Error adding dojo to database: {str(e)}", 500

@app.route('/add_dojo_to_normal', methods=['POST'])
def add_dojo_to_normal():
    dojo_name = request.form.get('dojo_name')
    address = request.form.get('address')
    city = request.form.get('city')
    age_range = request.form.get('age_range')

    print(f"Dojo Name: {dojo_name}, Address: {address}, City: {city}, Age Range: {age_range}")

    # Create a dictionary of parameters
    params = {
        'dojo_name': dojo_name,
        'address': address,
        'city': city,
        'age_range': age_range
    }

    # Build the confirmation URL with properly encoded parameters
    confirmation_url = f"http://localhost:5000/confirm_dojo?{urlencode(params)}"

    msg = Message(
        subject="New Dojo Listing for Verification",
        recipients=["dojofinderinfo@gmail.com"]
    )
    
    msg.body = f"""
    Please verify the following dojo details:

    Dojo Name: {dojo_name}
    Address: {address}
    City: {city}
    Age Range: {age_range}

    Click the link below to confirm and add this dojo to the database:
    {confirmation_url}
    """

    mail.send(msg)

    return redirect('/')

@app.route('/')
def home():
    return render_template('./homePage.html')


    
if __name__ == '__main__':
    app.run(debug=True)

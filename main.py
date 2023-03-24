from os import name
import firebase_admin
from flask import *
from firebase_admin import credentials, initialize_app, storage, db
import tempfile
import requests
import urllib3
import json
import fsspec
import secrets

# Init firebase with your credentials
cred = credentials.Certificate("signupsyatem-e20be6a93767.json")
db_app = initialize_app(credential=cred)
ref = db.reference("/users/nfc-app", url='https://signupsyatem-default-rtdb.firebaseio.com/')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'superb'

@app.route('/', methods=['POST', 'GET'])
def adddetails():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        linkedin = request.form['linkedin']
        product_image = request.files['image']
        temp = tempfile.NamedTemporaryFile(delete=False)
        product_image.save(temp.name)
        bucket = storage.bucket(name='signupsyatem.appspot.com', app=db_app)
        blob = bucket.blob(temp.name)
        blob.upload_from_filename(temp.name)
            # Opt : if you want to make public access from the URL
        blob.make_public()
        product_image = blob.public_url
        ref.push({
            'name': name,
            'email': email,
            'phone': phone,
            'linkedin': linkedin,
            'password': password,
            'image': product_image
        })
        return redirect(url_for('find'))
    if request.method == 'GET':
        return render_template('takeinput.html')
    
@app.route('/view/<user_id>', methods=['GET'])
def view(user_id):
    data = ref.child(user_id).get()
    message = "" + "/" + str(user_id)
    return render_template('profilesetup.html', data=data, message=message)

@app.route('/login', methods=['GET', 'POST'])   
def find():
    if request.method == 'POST':
        name = str(secrets.token_hex(nbytes=16))
        cred = credentials.Certificate("signupsyatem-e20be6a93767.json")
        print(name)
        db_app = initialize_app(credential=cred, name=name)
        ref = db.reference("/users/nfc-app", url='https://signupsyatem-default-rtdb.firebaseio.com/')
        user_data = ref.get()
        email = request.form['email']
        password = request.form['password']
        print(password)
        for key in user_data.keys():
            if user_data[key]['email'] == email and user_data[key]['password'] == password:
                return redirect('/view/' + key)
    if request.method == 'GET':
        return render_template('find.html')

if __name__ == "__main__":
    app.run(debug=True)
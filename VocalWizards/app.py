from flask import Flask,render_template,session,redirect,url_for,flash,request,send_file,jsonify
from datetime import timedelta
from flask_mail import Mail,Message
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms import validators,ValidationError
import os
import random
from spleeter.separator import Separator
import librosa
import numpy as np
import librosa.feature
import requests
import httpx
import shutil
import zipfile
import tempfile
import tensorflow as tf
import soundfile as sf
from pydub import AudioSegment
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'  # Fix the URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY']='random key'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='isuruchandika321@gmail.com'
app.config['MAIL_PASSWORD']='smot jwzf tpou qtax'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail=Mail(app)


db = SQLAlchemy(app)

class Users(db.Model):  # Fix the typo
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    code=db.Column(db.Integer, nullable=True)
    password = db.Column(db.String(100))

    def __init__(self,username,email,password):
        self.username=username
        self.email = email
        self.password=password

@app.route("/send",methods=["GET","POST"])
def send():
    if 'username' in session:
        return redirect(url_for("hello"))
    else:
        random_number=random.randint(1000, 9999)
        user_email = request.form["email"]
        session["trier"]=user_email
        user = Users.query.filter_by(email=user_email).first()
        if user:
                user.code = random_number
                db.session.commit()
        else:
            flash("The entered email doesn't register in the system!")
            return "hellow"
        msg=Message('OTP Vocal Wizards',sender='isuruchandika321@gmail.com',recipients=[user_email])
        msg.body= f"Hello user use this OTP code :{random_number} "
        mail.send(msg)
        return redirect(url_for("sendOTP"))


@app.route('/')
def hello():
    #session['username']="isuru"
    return render_template("home.html")

@app.route('/faq')
def faq():
    return render_template("faq.html")


@app.route("/login",methods=['GET','POST'])
def login():
    if 'username' in session:
        return redirect(url_for("hello"))
    if request.method == "POST":
        email=request.form["email"]
        password=request.form["password"]
        if email !="" and password !="":
    
            found_user = Users.query.filter_by(email=email).first() 
            if found_user and found_user.password==password:
                session["username"]=found_user.username
                session["email"] = found_user.email
                flash("user logged successfully!",category='success')
                return redirect(url_for("home"))
            else:
                flash("User not found! Incorrect email or password",'danger')
        else:
            if email=="" and password=="":
                flash("Email and password both required to login to the site",category='danger')
            else:
                if email=="":
                    flash("Email is required to login to the site",category='danger') 
                elif password=="":
                    flash("The password is required to login to the site",category='danger')
            
    return render_template("Login.html")

@app.route("/register", methods=['POST', 'GET'])
def register():
   
        if 'username' in session:
            return redirect(url_for("hello"))
        
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            if username !="" and email !="" and password !="":        
                new_user = Users(username, email, password)
                db.session.add(new_user)
                db.session.commit()
                flash("User registration completed!",category='success')
            else:
                if username=="" and email=="" and password=="":
                    flash("Username,Email,Password required!",category='danger')
                else:

                    if username=="":
                        flash("The username is required to register to the site",category='danger')
                    elif email=="":
                        flash("Email is required to register to the site",category='danger')
                    elif password=="":
                        flash("Password is required to register to the site",category='danger')
                
        return render_template("register.html")


@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("hello"))

@app.route("/equalizer")
def equalizer():
    if 'username' not in session: 
        flash("Login required to use the functionality!!", category="info")
        return redirect(url_for("login"))
    return render_template("EqualizerPage.html")

@app.route("/find")
def find():
    if 'username' in session:
        return redirect(url_for("hello"))
    return render_template("find.html")

@app.route("/contact")
def contact():
    if 'username' not in session:
        flash("Please login to use this functionality",category="info")
        return redirect(url_for("hello"))
    return render_template("contact.html")

@app.route("/aboutus")
def aboutUs():
    return render_template("AboutUs.html")


@app.route("/sendOTP")
def sendOTP():
    if 'username' in session:
        return redirect(url_for("hello"))
    flash("OTP sent successfully! Check the email",category='success')
    return render_template("sendOTP.html")

@app.route("/loginForm")
def loginForm():
    return render_template("login.html")

@app.route("/check", methods=["POST"])
def check():
    if request.method == "POST":
        code_OTP = request.form['OTP']
        user = Users.query.filter_by(code=code_OTP).first()

        if user and user.code == int(code_OTP):
            flash("OTP is valid! Change the password from here!",category="success")
            # Perform any additional actions you need upon successful validation
            return redirect(url_for("retype"))
        else:
            flash("Invalid OTP. Please try again.",category="danger")
            return redirect(url_for("sendOTP"))
        
@app.route("/view")
def view():
    return render_template("view.html",values=Users.query.all())

@app.route("/retype")
def retype():
    if 'username' in session:
        redirect(url_for("hello"))

    return render_template("retypepass.html")

@app.route("/combine")
def test():
    if 'username' not in session:
        flash("Please login to the site to use vocal replacement ",category='info')
        return redirect(url_for("features"))
    return render_template("plus.html")

@app.route("/check2",methods=["POST"])
def check2():
    if request.method=="POST":
        password1=request.form['password1']
        password2=request.form['password2']
        if password1 !="" and password2 !="":
            if(password1==password2):
                user = Users.query.filter_by(email=session['trier']).first()
                if user:
                    user.password = password1
                    db.session.commit()
                    flash("Password changed successfully!",category="success")
                    return redirect(url_for("hello"))
            

            else:
                flash("Missmatch Password!",category="danger")
                return redirect(url_for("retype")) 
        else:
            flash("Password retyping required!",category="danger")
            return redirect(url_for("retype"))

@app.route("/features",methods=["POST","GET"])
def features():
    return render_template("Features.html")

@app.route("/isolation")
def isolation():
    if 'username' not in session:
        flash("login to the site to use AI powered vocal isolation",category="info")
        return redirect(url_for("features"))
    return render_template("Vocal_iso.html")

@app.route('/reverb')
def RenderReverbPage():
    if 'username' not in session:
        flash("Login to the site to use Reverb functionality")
        return redirect(url_for("features"))
    return render_template("reverb.html")

@app.route('/Audio_Analysing')
def AudioAnalyze():
    if 'username' not in session:
        flash("Login to the site to use this Audio Analysing functionality",category="info")
        return redirect(url_for("features"))
    return render_template("audioAnalyzer.html")#add themiyas analysing page here

@app.route('/vocal_isolation', methods=['POST'])
def vocal_isolation():
    if 'audioFile' not in request.files:
        return render_template('index.html', isolated_vocals=None)

    audio_file = request.files['audioFile']

    if audio_file.filename == '':
        return render_template('index.html', isolated_vocals=None)

    # Save the uploaded audio file temporarily
    file_path = 'temp_audio.wav'
    audio_file.save(file_path)

    # Perform vocal isolation
    isolated_vocals_path = isolate_vocals(file_path)

    # Serve the zip file for download
    return send_file(isolated_vocals_path, as_attachment=True)

def isolate_vocals(file_path):
    # Local path to the pretrained model directory
    model_path = 'spleeter/configs/2stems/base_config.json'

    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Load Spleeter separator model
        separator = Separator(model_path)

        # Process the audio file
        audio_input = file_path
        prediction = separator.separate_to_file(audio_input, temp_dir)

        # The isolated vocals will be in the 'vocals.wav' file
        isolated_vocals_path = os.path.join(temp_dir, 'vocals.wav')

        # Create a zip file containing the output files
        zip_file_path = 'output.zip'
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, temp_dir))

    return zip_file_path

@app.route('/reverb', methods=['POST'])
def add_reverb():
    if 'audioFile' not in request.files:
        return render_template('index.html', reverb_added=None)

    audio_file = request.files['audioFile']

    if audio_file.filename == '':
        return render_template('index.html', reverb_added=None)

    # Save the uploaded audio file temporarily
    input_file_path = 'temp_audio.wav'
    audio_file.save(input_file_path)

    # Add reverb to the audio file
    output_file_path = add_reverb_to_audio(input_file_path)

    # Serve the modified audio file for download
    return send_file(output_file_path, as_attachment=True)

def add_reverb_to_audio(input_file_path):
    # Load audio file using librosa
    y, sr = librosa.load(input_file_path, sr=None)

    # Add reverb (adjust the parameters as needed)
    y_reverb = librosa.effects.preemphasis(y, coef=0.97)

    # Save the modified audio file using soundfile
    output_file_path = 'reverb_added_audio.wav'
    sf.write(output_file_path, y_reverb, sr)

    return output_file_path

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'audioFile' not in request.files:
        return render_template('index.html', mid_value=None, low_value=None, high_value=None,
                               mid_suggestion=None, low_suggestion=None, high_suggestion=None)

    audio_file = request.files['audioFile']

    if audio_file.filename == '':
        return render_template('index.html', mid_value=None, low_value=None, high_value=None,
                               mid_suggestion=None, low_suggestion=None, high_suggestion=None)

    # Save the uploaded audio file temporarily
    file_path = 'temp_audio.wav'
    audio_file.save(file_path)

    # Perform audio analysis
    mid_value, low_value, high_value, mid_suggestion, low_suggestion, high_suggestion = analyze_audio(file_path)

    print("Mid Suggestion:", mid_suggestion)
    print("Low Suggestion:", low_suggestion)
    print("High Suggestion:", high_suggestion)

    return render_template('Analysis-Results1.html', mid_value=mid_value, low_value=low_value, high_value=high_value,
                           mid_suggestion=mid_suggestion, low_suggestion=low_suggestion, high_suggestion=high_suggestion)

def analyze_audio(file_path):
    # Load audio file using librosa
    y, sr = librosa.load(file_path)

    # Extract features using librosa
    mfccs = librosa.feature.mfcc(y=y, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

    # Use the extracted features for analysis
    mid_value = np.mean(mfccs)
    low_value = np.min(spectral_contrast)
    high_value = np.max(spectral_contrast)

    # Suggested adjustments
    mid_target = 0.5  # Replace with your desired target for mid value
    low_target = -0.5  # Replace with your desired target for low value
    high_target = 0.5 

    mid_adjustment = mid_target - mid_value
    low_adjustment = low_target - low_value
    high_adjustment = high_target - high_value

    mid_suggestion = f"Increase mid value by {abs(mid_adjustment):.4f} for better quality."
    low_suggestion = f"Decrease low value by {abs(low_adjustment):.4f} for better quality."
    high_suggestion = f"Increase high value by {abs(high_adjustment):.4f} for better quality."

    return mid_value, low_value, high_value, mid_suggestion, low_suggestion, high_suggestion

@app.route('/messageSent',methods=["POST"])
def messageSent():
    if 'username' not in session:
        redirect(url_for("hello"))
    
    user_name=request.form['name']
    user_email = request.form['email']
    user_message = request.form['message']
    if user_name=='' and user_email=='' and user_message=='':
        flash("Enter username,email and messaage to send us ",category="danger")
        return redirect(url_for("contact"))
    
    elif user_name =='':
        flash("name is required to send message",category="danger")
        return redirect(url_for("contact"))
    elif user_email =="":
        flash("Email is required to send message",category="danger")
        return redirect(url_for("contact"))
    elif user_message == "":
        flash("Enter the email what you have want",category="danger")
        return redirect(url_for("contact"))
    else:
        # Create and send the email
        msg = Message(f"New Message from {user_name}", sender=user_email, recipients=['isuruchandika321@gmail.com'])
        msg.body = f"Sender name : {user_name}\n\nMessage from {user_email}:\n\n{user_message}"

        try:
            mail.send(msg)
            flash('Message sent successfully!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            flash(f'Error sending message: {str(e)}', 'error')
            return redirect(url_for('contact'))


# Define default parameters
DEFAULT_THRESHOLD = -20  # dBFS
DEFAULT_RATIO = 4
DEFAULT_ATTACK_TIME = 0.1  # seconds
DEFAULT_RELEASE_TIME = 0.5  # seconds
DEFAULT_GAIN = 0  # dB

def read_audio(input_file):
    try:
        # Load audio file
        y, sr = librosa.load(input_file, sr=None)
        return y, sr
    except Exception as e:
        return None, None

def divide_into_frames(y, frame_size):
    # Divide audio into frames
    frames = []
    num_frames = len(y) // frame_size
    for i in range(num_frames):
        frame = y[i * frame_size : (i + 1) * frame_size]
        frames.append(frame)
    return frames

def calculate_gain_reduction(frame, threshold, ratio):
    # Calculate gain reduction for a single frame
    rms = np.sqrt(np.mean(frame**2))
    if rms > threshold:
        gain_reduction = (rms - threshold) / ratio
    else:
        gain_reduction = 0
    return gain_reduction

def apply_attack_and_release(gain_reduction, attack_time, release_time, previous_gain_reduction=0):
    # Apply attack and release
    if gain_reduction > previous_gain_reduction:
        gain_reduction = previous_gain_reduction + (attack_time * (gain_reduction - previous_gain_reduction))
    else:
        gain_reduction = previous_gain_reduction + (release_time * (gain_reduction - previous_gain_reduction))
    return gain_reduction

def apply_makeup_gain(frame, gain_reduction, gain):
    # Apply makeup gain
    makeup_gain = np.power(10, (gain_reduction + gain) / 20)  # Convert gain reduction to linear scale
    return frame * makeup_gain

def output_audio(compressed_frames, output_file, sr):
    # Concatenate frames and save the compressed audio
    compressed_audio = np.concatenate(compressed_frames)
    sf.write(output_file, compressed_audio, sr)



@app.route("/compressor")
def compressor():
    if 'username' not in session:
        flash("Loggin to the site to use this automatic audio mixer",category="info")
        return redirect(url_for("features"))
    return render_template("compressor.html")

@app.route('/compress', methods=['POST'])
def compress():
    
    try:
        # Get uploaded file
        audio_file = request.files['audio_file']

        # Get parameters from the form or use defaults
        threshold_db = float(request.form.get('threshold', DEFAULT_THRESHOLD))
        ratio = float(request.form.get('ratio', DEFAULT_RATIO))
        attack_time = float(request.form.get('attack_time', DEFAULT_ATTACK_TIME))
        release_time = float(request.form.get('release_time', DEFAULT_RELEASE_TIME))
        gain = float(request.form.get('gain', DEFAULT_GAIN))

        # Save the uploaded file
        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)  # Create the upload folder if it doesn't exist

        input_file = os.path.join(upload_folder, audio_file.filename)
        audio_file.save(input_file)

        # Parameters
        frame_size = 1024

        # Read Audio Input
        y, sr = read_audio(input_file)

        if y is None or sr is None:
            return jsonify({'error': 'Failed to read audio file.'}), 500

        # Divide Audio into Frames
        frames = divide_into_frames(y, frame_size)

        # Calculate Gain Reduction
        compressed_frames = []
        previous_gain_reduction = 0
        for frame in frames:
            gain_reduction = calculate_gain_reduction(frame, threshold_db, ratio)

            # Apply Attack and Release
            gain_reduction = apply_attack_and_release(gain_reduction, attack_time, release_time, previous_gain_reduction)
            previous_gain_reduction = gain_reduction

            # Apply Makeup Gain
            compressed_frame = apply_makeup_gain(frame, -gain_reduction, gain)  # Include the gain parameter here
            compressed_frames.append(compressed_frame)

        # Output the Compressed Audio
        output_folder = 'output'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_file = os.path.abspath(os.path.join(output_folder, 'compressed_audio.wav'))
        output_audio(compressed_frames, output_file, sr)

        return send_file(output_file, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
#combination codes
@app.route('/combine', methods=['POST'])
def combine():
    try:
        model_path = 'spleeter/configs/2stems/base_config.json'

        # Get uploaded files
        tone_file = request.files['tone']
        music_file = request.files['music']

        # Save uploaded files
        tone_path = 'uploads/tone.wav'
        music_path = 'uploads/music.wav'
        tone_file.save(os.path.join(tone_path))
        music_file.save(os.path.join(music_path))

        # Combine tone and music using spleeter
        separator = Separator(model_path)

        # Use system's temporary directory
        output_path = tempfile.mkdtemp()

        separator.separate_to_file(os.path.join(tone_path), output_path)

        # Combine the separated vocals with the original music
        combined_path = os.path.join(output_path, 'vocals', 'accompaniment.wav')

        # Create the 'pro' folder inside the temporary directory
        pro_folder = os.path.join(output_path, 'pro')
        os.makedirs(pro_folder, exist_ok=True)

        # Specify the absolute path for the output file
        output_file_path = os.path.join(pro_folder, 'output.wav')

        # Combine tone and music into one audio file
        combine_audio(tone_path, music_path, output_file_path)

        # Return the combined file for download
        return send_file(output_file_path, as_attachment=True)

    except Exception as e:
        return str(e)

def combine_audio(tone_path, music_path, output_path):
    # Load audio files
    tone = AudioSegment.from_file(tone_path)
    music = AudioSegment.from_file(music_path)

    # Ensure both audio files have the same length
    if len(tone) > len(music):
        tone = tone[:len(music)]
    elif len(tone) < len(music):
        music = music[:len(tone)]

    # Combine audio files
    combined_audio = tone.overlay(music)

    # Export the combined audio to the specified output path
    combined_audio.export(output_path, format="wav")

#code for the equalizer part updated the correct code
      
UPLOAD_FOLDER = 'uploadsEq'
PROCESSED_FOLDER = 'processedEq'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

def process_audio(audio_path, bass_gain, midrange_gain, treble_gain):
    # Load audio file
    y, sr = librosa.load(audio_path, sr=None)

    # Apply equalizer settings
    y_bass = librosa.effects.preemphasis(y, coef=bass_gain)
    y_midrange = librosa.effects.preemphasis(y, coef=midrange_gain)
    y_treble = librosa.effects.preemphasis(y, coef=treble_gain)

    # Combine channels
    y_combined = (y_bass + y_midrange + y_treble) / 3.0

    return y_combined, sr

@app.route('/equalizing123')
def index():
    if 'username' not in session:
        flash("Loggin to the site to use this automatic audio mixer",category="info")
        return redirect(url_for("features"))
    return render_template('equalizingPage.html')

@app.route('/equalizerProcessing1', methods=['POST'])
def equalizer123():
    # Get uploaded audio file and equalizer settings
    audio_file = request.files['audio']
    bass_gain = float(request.form['bass'])
    midrange_gain = float(request.form['midrange'])
    treble_gain = float(request.form['treble'])

    # Save uploaded audio file
    audio_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(audio_path)

    # Process audio
    processed_audio, sr = process_audio(audio_path, bass_gain, midrange_gain, treble_gain)

    # Save processed audio
    processed_audio_path = os.path.join(PROCESSED_FOLDER, audio_file.filename.split('.')[0] + '.wav')
    sf.write(processed_audio_path, processed_audio, sr)

    # Serve processed audio for download
    return send_file(processed_audio_path, as_attachment=True)


#multiband dynamic feature code
@app.route('/mutibandDynamic')
def multibandDynamic():
    if 'username' not in session:
        flash("Loggin to the site to use this automatic audio mixer",category="info")
        return redirect(url_for("features"))
    return render_template('master.html')

@app.route('/multibandProsessing', methods=['POST'])
def multibandProcess():
    # Get the uploaded audio file
    audio_file = request.files['audio']

    # Read the audio file
    audio_data, sr = librosa.load(audio_file, sr=None)

    # Perform multiband dynamics processing
    processed_audio = multiband_dynamics(audio_data)

    # Return the processed audio as a downloadable file
    processed_wav = io.BytesIO()
    sf.write(processed_wav, processed_audio, sr, format='wav')
    processed_wav.seek(0)

    return send_file(
        processed_wav,
        mimetype='audio/wav',
        as_attachment=True,
        download_name='processed_audio.wav'
    )




def multiband_dynamics(audio_data, num_bands=30, threshold=80, ratio=60):
    # Split the audio into frequency bands
    stft = librosa.stft(audio_data)
    bands = np.array_split(stft, num_bands, axis=0)

    # Apply dynamics processing to each band
    processed_bands = []
    for band in bands:
        # Compute energy in each frequency band
        band_energy = np.mean(np.abs(band), axis=0)
        
        # Compute gain based on energy and threshold
        gain = np.ones_like(band_energy)
        gain[band_energy > threshold] = 10 + (ratio - 10) * ((band_energy[band_energy > threshold] - threshold) / threshold)
        
        # Transpose gain to match the shape of the band
        gain = gain.T

        # Apply gain to the band
        processed_band = band * gain
        processed_bands.append(processed_band)

    # Combine the processed bands back into a single audio signal
    processed_audio = librosa.istft(np.concatenate(processed_bands, axis=0))
    return processed_audio





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5000)

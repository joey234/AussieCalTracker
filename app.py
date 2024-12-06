from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import io
import os
from datetime import datetime, date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aussiecal.db'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    food_entries = db.relationship('FoodEntry', backref='user', lazy=True)

class FoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_type = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    serving_size = db.Column(db.String(50))
    image_path = db.Column(db.String(200))
    date_added = db.Column(db.Date, nullable=False, default=date.today)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def estimate_calories(image):
    # TODO: Implement actual calorie estimation using ML model
    # For demo purposes, returning a mock response
    return {
        "estimated_calories": 350,
        "confidence": 0.85,
        "food_type": "Australian meat pie",
        "serving_size": "1 pie (175g)"
    }

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    daily_entries = FoodEntry.query.filter_by(
        user_id=current_user.id,
        date_added=today
    ).order_by(FoodEntry.timestamp.desc()).all()
    
    total_calories = sum(entry.calories for entry in daily_entries)
    return render_template('dashboard.html', 
                         entries=daily_entries, 
                         total_calories=total_calories)

@app.route('/analyze', methods=['POST'])
@login_required
def analyze_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Read and process the image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Save the image with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'food_{timestamp}.jpg'
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)
        
        # Get calorie estimation
        result = estimate_calories(image)
        
        # Save to database
        food_entry = FoodEntry(
            user_id=current_user.id,
            food_type=result['food_type'],
            calories=result['estimated_calories'],
            serving_size=result['serving_size'],
            image_path=filename
        )
        db.session.add(food_entry)
        db.session.commit()
        
        return jsonify(result)
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = FoodEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if entry.image_path:
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, entry.image_path))
        except:
            pass
    
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True) 
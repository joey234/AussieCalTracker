from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import date
from app.models import FoodEntry
from app.services.calorie_estimator import estimate_calories
from app.utils.image_utils import allowed_file, save_image, delete_image
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    daily_entries = FoodEntry.query.filter_by(
        user_id=current_user.id,
        date_added=date.today()
    ).order_by(FoodEntry.timestamp.desc()).all()
    
    total_calories = sum(entry.calories for entry in daily_entries)
    return render_template('dashboard.html', 
                         entries=daily_entries, 
                         total_calories=total_calories)

@main_bp.route('/analyze-image', methods=['POST'])
@login_required
def analyze_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        image_path = save_image(file)
        if not image_path:
            return jsonify({'error': 'Error saving image'}), 500
        
        # Get calorie estimation
        result = estimate_calories(file)
        
        # Save to database
        food_entry = FoodEntry(
            user_id=current_user.id,
            food_type=result["food_type"],
            calories=result["estimated_calories"],
            serving_size=result["serving_size"],
            image_path=image_path,
            description=result.get("description"),
            is_australian=result.get("is_australian", False),
            australian_brands=result.get("australian_brands", []),
            suggestions=result.get("suggestions", []),
            confidence=result.get("confidence", 0.0)
        )
        db.session.add(food_entry)
        db.session.commit()
        
        return jsonify(result)
    
    return jsonify({'error': 'Invalid file type'}), 400

@main_bp.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = FoodEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete the image file if it exists
    if entry.image_path:
        delete_image(entry.image_path)
    
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('main.dashboard')) 
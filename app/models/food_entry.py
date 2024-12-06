from datetime import datetime, date
from app import db

class FoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_type = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    serving_size = db.Column(db.String(50))
    image_path = db.Column(db.String(200))
    date_added = db.Column(db.Date, nullable=False, default=date.today)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # New fields from Gemini
    description = db.Column(db.Text)
    is_australian = db.Column(db.Boolean, default=False)
    australian_brands = db.Column(db.JSON)  # Stored as JSON array
    suggestions = db.Column(db.JSON)  # Stored as JSON array
    confidence = db.Column(db.Float)

    def to_dict(self):
        return {
            'id': self.id,
            'food_type': self.food_type,
            'calories': self.calories,
            'serving_size': self.serving_size,
            'image_path': self.image_path,
            'date_added': self.date_added.isoformat(),
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'is_australian': self.is_australian,
            'australian_brands': self.australian_brands or [],
            'suggestions': self.suggestions or [],
            'confidence': self.confidence
        } 
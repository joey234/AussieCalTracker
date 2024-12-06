# AussieCalTracker

A web application for tracking calories specific to Australian food products. This demo version can analyze food images and estimate their caloric content.

## Features

- Upload food images
- Get instant calorie estimations
- Australian-specific food recognition
- Clean and modern user interface

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Click the "Choose Image" button
2. Select a food image (JPG or PNG)
3. Wait for the analysis
4. View the estimated calories and food information

## Note

This is a demo version with mock calorie estimation. For production use, you would need to:
1. Implement a proper machine learning model for Australian food recognition
2. Add a database of Australian food products and their nutritional information
3. Implement user authentication and history tracking
4. Add more robust error handling and validation

## Future Improvements

- Integration with Australian food databases
- Support for multiple food items in one image
- Nutritional information beyond calories
- User accounts and history tracking
- Mobile app version 
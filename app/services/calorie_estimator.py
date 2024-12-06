import os
import google.generativeai as genai
from PIL import Image
import io
from flask import current_app
import json
import re

# Configure Gemini API
def configure_genai():
    api_key = current_app.config['GOOGLE_API_KEY']
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in configuration")
    genai.configure(api_key=api_key)

class FoodRecognizer:
    def __init__(self):
        """Initialize the food recognizer."""
        # Initialize Gemini model
        configure_genai()
        # Use gemini-1.5-flash for faster responses
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_food_image(self, image):
        """
        Analyze food image using Gemini Vision API.
        Returns detailed information about the food items.
        """
        prompt = """
        You are an Australian food expert. Analyze this food image and provide the following information in valid JSON format:
        {
            "food_items": [
                {
                    "name": "Food item name (be specific about Australian context)",
                    "portion_size": "Specific portion size in grams or standard measures",
                    "is_australian": true/false,
                    "calories": estimated calories as number,
                    "confidence": confidence level between 0 and 1,
                    "description": "Brief description including Australian context if relevant"
                }
            ],
            "total_calories": sum of all food items calories,
            "is_typical_australian": true/false,
            "australian_brands": ["any recognized Australian brands"],
            "confidence": overall confidence level between 0 and 1,
            "suggestions": ["any relevant dietary or cultural notes about this food in Australian context"]
        }

        Focus on Australian food items, portions, and brands. If you recognize specific Australian products or dishes, include them.
        Be specific about portion sizes and calorie estimates. If multiple items are present, list them separately.
        Ensure the response is in valid JSON format only, no additional text.
        """
        
        try:
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format or 'JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            # Create the image part
            image_part = {
                "mime_type": "image/jpeg",
                "data": img_byte_arr
            }

            # Generate content
            response = self.model.generate_content(
                contents=[prompt, image_part]
            )

            # Get the response text
            if response and response.text:
                return response.text
            else:
                raise ValueError("Empty response from Gemini")

        except Exception as e:
            print(f"Error in Gemini analysis: {str(e)}")
            return None

    def extract_json_from_text(self, text):
        """Extract JSON from text that might contain additional content."""
        try:
            # Try to find JSON pattern in the text
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            return None
        except Exception as e:
            print(f"Error extracting JSON: {str(e)}")
            return None

    def process_gemini_response(self, response_text):
        """Process the Gemini response and format it for our application."""
        try:
            if not response_text:
                raise ValueError("Empty response from Gemini")

            # Parse JSON from response
            data = self.extract_json_from_text(response_text)
            if not data:
                raise ValueError("Could not parse JSON from response")

            # Get the main food item (first one or most confident one)
            food_items = data.get("food_items", [])
            if not food_items:
                raise ValueError("No food items found in response")

            # Sort by confidence and get the highest confidence item
            main_item = max(food_items, key=lambda x: x.get("confidence", 0))

            # Format the response
            result = {
                "food_type": main_item["name"],
                "calories": main_item["calories"],
                "serving_size": main_item["portion_size"],
                "confidence": main_item["confidence"],
                "is_australian": main_item.get("is_australian", False),
                "description": main_item.get("description", ""),
                "total_calories": data.get("total_calories", main_item["calories"]),
                "australian_brands": data.get("australian_brands", []),
                "suggestions": data.get("suggestions", [])
            }

            return result

        except Exception as e:
            print(f"Error processing Gemini response: {str(e)}")
            print(f"Original response: {response_text}")
            return None

def estimate_calories(image_file):
    """
    Estimate calories from an image using Gemini Vision API.
    """
    try:
        # Initialize recognizer
        recognizer = FoodRecognizer()
        
        # Convert image file to PIL Image
        image = Image.open(image_file)
        
        # Analyze image with Gemini
        analysis = recognizer.analyze_food_image(image)
        
        # Process Gemini's response
        result = recognizer.process_gemini_response(analysis)
        
        if not result:
            raise ValueError("Failed to process Gemini response")
        
        return {
            "estimated_calories": result["calories"],
            "confidence": result["confidence"],
            "food_type": result["food_type"],
            "serving_size": result["serving_size"],
            "is_australian": result["is_australian"],
            "description": result["description"],
            "total_calories": result["total_calories"],
            "australian_brands": result["australian_brands"],
            "suggestions": result["suggestions"]
        }
        
    except Exception as e:
        print(f"Error in calorie estimation: {str(e)}")
        return {
            "error": str(e),
            "estimated_calories": 0,
            "confidence": 0,
            "food_type": "Unknown",
            "serving_size": "Unknown",
            "is_australian": False,
            "description": "",
            "total_calories": 0,
            "australian_brands": [],
            "suggestions": []
        } 
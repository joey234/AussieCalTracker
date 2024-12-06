from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Enable debug mode and hot reloading
    app.run(
        host='0.0.0.0',  # Make the server publicly available
        port=2000,       # Port number
        debug=True,      # Enable debug mode
        use_reloader=True  # Enable hot reloading
    ) 
"""
Application Entry Point
Runs the Flask development server.
"""

from app import create_app
import logging

# Create Flask application
app = create_app()

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info("Starting LyfterCook development server on http://localhost:5000")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

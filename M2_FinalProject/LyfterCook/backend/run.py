"""
Application Entry Point
Runs the Flask development server.
"""

from app import create_app
import logging
import sys
import traceback

# Create Flask application
try:
    app = create_app()
except Exception as e:
    print(f"FATAL ERROR creating app: {e}")
    traceback.print_exc()
    sys.exit(1)

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info("Starting LyfterCook development server on http://localhost:5000")
    print("=" * 60)
    print("LyfterCook Server Starting...")
    print("URL: http://localhost:5000")
    print("Health Check: http://localhost:5000/health")
    print("Test Endpoint: http://localhost:5000/test")
    print("=" * 60)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False,  # Disable reloader to prevent crashes
            threaded=True  # Enable threading to prevent blocking
        )
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        print(f"\n\nFATAL SERVER ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Simple Production Startup Script
"""

import os
import sys

def main():
    """Start production server"""
    print('🚀 STARTING PRODUCTION SERVER')
    print('=' * 50)
    
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    
    # Import and create app
    sys.path.insert(0, '.')
    try:
        from app_prod import create_app
        app = create_app()
        
        print('✅ Application created successfully')
        print('🌐 Starting server on http://0.0.0.0:5000')
        print('📊 Environment: PRODUCTION')
        print('🔒 Server will run with Gunicorn behind proxy')
        
        # Start the application
        app.run(host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f'❌ Failed to start application: {e}')
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

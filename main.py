#!/usr/bin/env python3
"""Main entry point for the WLED Controller application."""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))
    reload = os.getenv('RELOAD', 'false').lower() == 'true'
    
    print(f"Starting WLED Controller on http://{host}:{port}")
    print(f"WLED Host: {os.getenv('WLED_HOST', 'http://wled.local')}")
    print(f"Reload enabled: {reload}")
    
    # Start the FastAPI server
    uvicorn.run(
        'src.app:app',
        host=host,
        port=port,
        reload=reload,
        log_level='info'
    ) 
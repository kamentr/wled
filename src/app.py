"""FastAPI web application for WLED control."""

import logging
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from .wled_client import WLEDClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title='WLED Controller', version='1.0.0')

# Initialize WLED client
wled_host = os.getenv('WLED_HOST', 'http://wled.local')
wled_client = WLEDClient(host=wled_host)

# Mount static files
app.mount('/static', StaticFiles(directory='static'), name='static')

# Setup templates
templates = Jinja2Templates(directory='templates')

# Pydantic models for request validation
class BrightnessRequest(BaseModel):
    brightness: int

class ColorRequest(BaseModel):
    red: int
    green: int
    blue: int
    white: int = 0

class EffectRequest(BaseModel):
    effect_id: int

class SpeedRequest(BaseModel):
    speed: int

class IntensityRequest(BaseModel):
    intensity: int


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main web UI."""
    return templates.TemplateResponse('index.html', {'request': request})


@app.get('/api/state')
async def get_state():
    """Get current WLED state."""
    state = wled_client.get_state()
    if state is None:
        raise HTTPException(status_code=503, detail='WLED device not reachable')
    return state


@app.get('/api/effects')
async def get_effects():
    """Get available WLED effects."""
    effects = wled_client.get_effects()
    if effects is None:
        raise HTTPException(status_code=503, detail='WLED device not reachable')
    
    # Filter effects to only include those with valid IDs (0-101)
    # This matches the validation in the POST /api/effect endpoint
    valid_effects_with_ids = []
    for i, effect in enumerate(effects):
        if 0 <= i <= 101:
            valid_effects_with_ids.append({'id': i, 'name': effect})
    
    # Sort effects alphabetically by name while preserving IDs
    valid_effects_with_ids.sort(key=lambda x: x['name'])
    
    return {'effects': valid_effects_with_ids}


@app.post('/api/power')
async def toggle_power():
    """Toggle WLED power on/off."""
    success = wled_client.toggle()
    if not success:
        raise HTTPException(status_code=503, detail='Failed to toggle power')
    return {'success': True}


@app.post('/api/power/on')
async def turn_on():
    """Turn WLED lights on."""
    success = wled_client.turn_on()
    if not success:
        raise HTTPException(status_code=503, detail='Failed to turn on')
    return {'success': True}


@app.post('/api/power/off')
async def turn_off():
    """Turn WLED lights off."""
    success = wled_client.turn_off()
    if not success:
        raise HTTPException(status_code=503, detail='Failed to turn off')
    return {'success': True}


@app.post('/api/brightness')
async def set_brightness(request: BrightnessRequest):
    """Set WLED brightness."""
    if not 0 <= request.brightness <= 255:
        raise HTTPException(status_code=400, detail='Brightness must be 0-255')
    
    success = wled_client.set_brightness(request.brightness)
    if not success:
        raise HTTPException(status_code=503, detail='Failed to set brightness')
    return {'success': True}


@app.post('/api/color')
async def set_color(request: ColorRequest):
    """Set WLED color."""
    for color, name in [(request.red, 'red'), (request.green, 'green'), 
                        (request.blue, 'blue'), (request.white, 'white')]:
        if not 0 <= color <= 255:
            raise HTTPException(
                status_code=400, 
                detail=f'{name.capitalize()} must be 0-255'
            )
    
    success = wled_client.set_color(request.red, request.green, request.blue, request.white)
    if not success:
        raise HTTPException(status_code=503, detail='Failed to set color')
    return {'success': True}


@app.post('/api/effect')
async def set_effect(request: EffectRequest):
    """Set WLED effect."""
    if not 0 <= request.effect_id <= 101:
        raise HTTPException(status_code=400, detail='Effect ID must be 0-101')
    
    success = wled_client.set_effect(request.effect_id)
    if not success:
        raise HTTPException(status_code=503, detail='Failed to set effect')
    return {'success': True}


@app.post('/api/effect/speed')
async def set_effect_speed(request: SpeedRequest):
    """Set WLED effect speed."""
    if not 0 <= request.speed <= 255:
        raise HTTPException(status_code=400, detail='Speed must be 0-255')
    
    success = wled_client.set_effect_speed(request.speed)
    if not success:
        raise HTTPException(status_code=503, detail='Failed to set speed')
    return {'success': True}


@app.post('/api/effect/intensity')
async def set_effect_intensity(request: IntensityRequest):
    """Set WLED effect intensity."""
    if not 0 <= request.intensity <= 255:
        raise HTTPException(status_code=400, detail='Intensity must be 0-255')
    
    success = wled_client.set_effect_intensity(request.intensity)
    if not success:
        raise HTTPException(status_code=503, detail='Failed to set intensity')
    return {'success': True}


@app.get('/api/health')
async def health_check():
    """Health check endpoint."""
    connected = wled_client.is_connected()
    return {
        'status': 'healthy' if connected else 'unhealthy',
        'wled_connected': connected,
        'wled_host': wled_host
    } 
"""WLED API client for controlling WLED lights."""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError


class WLEDClient:
    """Client for interacting with WLED devices via JSON API."""
    
    def __init__(self, host: str = 'http://wled.local', timeout: int = 5):
        """
        Initialize WLED client.
        
        Args:
            host: WLED device host address (default: http://wled.local)
            timeout: Request timeout in seconds (default: 5)
        """
        self.host = host.rstrip('/')
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
    def _make_request(self, method: str, endpoint: str, 
                     data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make HTTP request to WLED device.
        
        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint
            data: Request data for POST requests
            
        Returns:
            Response JSON data or None if request failed
        """
        url = f'{self.host}{endpoint}'
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, timeout=self.timeout)
            else:
                raise ValueError(f'Unsupported HTTP method: {method}')
                
            response.raise_for_status()
            return response.json()
            
        except (RequestException, Timeout, ConnectionError) as e:
            self.logger.error(f'Request failed: {e}')
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f'Invalid JSON response: {e}')
            return None
            
    def get_state(self) -> Optional[Dict]:
        """
        Get current WLED state.
        
        Returns:
            Current state dictionary or None if request failed
        """
        return self._make_request('GET', '/json/state')
        
    def get_effects(self) -> Optional[List[str]]:
        """
        Get available WLED effects.
        
        Returns:
            List of effect names or None if request failed
        """
        response = self._make_request('GET', '/json/effects')
        if response:
            # Handle both formats: direct array or wrapped in object
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and 'effects' in response:
                return response['effects']
        return None
        
    def turn_on(self) -> bool:
        """
        Turn WLED lights on.
        
        Returns:
            True if successful, False otherwise
        """
        data = {'on': True}
        response = self._make_request('POST', '/json/state', data)
        return response is not None
        
    def turn_off(self) -> bool:
        """
        Turn WLED lights off.
        
        Returns:
            True if successful, False otherwise
        """
        data = {'on': False}
        response = self._make_request('POST', '/json/state', data)
        return response is not None
        
    def toggle(self) -> bool:
        """
        Toggle WLED lights on/off.
        
        Returns:
            True if successful, False otherwise
        """
        current_state = self.get_state()
        if current_state is None:
            return False
            
        new_state = not current_state.get('on', False)
        data = {'on': new_state}
        response = self._make_request('POST', '/json/state', data)
        return response is not None
        
    def set_brightness(self, brightness: int) -> bool:
        """
        Set WLED brightness.
        
        Args:
            brightness: Brightness value (0-255)
            
        Returns:
            True if successful, False otherwise
        """
        if not 0 <= brightness <= 255:
            self.logger.error(f'Invalid brightness value: {brightness}')
            return False
            
        data = {'bri': brightness}
        response = self._make_request('POST', '/json/state', data)
        return response is not None
        
    def set_color(self, red: int, green: int, blue: int, 
                  white: int = 0) -> bool:
        """
        Set WLED primary color.
        
        Args:
            red: Red value (0-255)
            green: Green value (0-255)
            blue: Blue value (0-255)
            white: White value (0-255, default: 0)
            
        Returns:
            True if successful, False otherwise
        """
        for color, name in [(red, 'red'), (green, 'green'), 
                           (blue, 'blue'), (white, 'white')]:
            if not 0 <= color <= 255:
                self.logger.error(f'Invalid {name} value: {color}')
                return False
                
        data = {
            'seg': [{
                'col': [[red, green, blue, white]]
            }]
        }
        response = self._make_request('POST', '/json/state', data)
        return response is not None
        
    def set_effect(self, effect_id: int) -> bool:
        """
        Set WLED effect.
        
        Args:
            effect_id: Effect index (0-101)
            
        Returns:
            True if successful, False otherwise
        """
        if not 0 <= effect_id <= 101:
            self.logger.error(f'Invalid effect ID: {effect_id}')
            return False
            
        data = {
            'seg': [{
                'fx': effect_id
            }]
        }
        response = self._make_request('POST', '/json/state', data)
        return response is not None
        
    def set_effect_speed(self, speed: int) -> bool:
        """
        Set WLED effect speed.
        
        Args:
            speed: Speed value (0-255)
            
        Returns:
            True if successful, False otherwise
        """
        if not 0 <= speed <= 255:
            self.logger.error(f'Invalid speed value: {speed}')
            return False
            
        data = {
            'seg': [{
                'sx': speed
            }]
        }
        response = self._make_request('POST', '/json/state', data)
        return response is not None
        
    def set_effect_intensity(self, intensity: int) -> bool:
        """
        Set WLED effect intensity.
        
        Args:
            intensity: Intensity value (0-255)
            
        Returns:
            True if successful, False otherwise
        """
        if not 0 <= intensity <= 255:
            self.logger.error(f'Invalid intensity value: {intensity}')
            return False
            
        data = {
            'seg': [{
                'ix': intensity
            }]
        }
        response = self._make_request('POST', '/json/state', data)
        return response is not None
        
    def is_connected(self) -> bool:
        """
        Check if WLED device is reachable.
        
        Returns:
            True if device is reachable, False otherwise
        """
        return self.get_state() is not None 
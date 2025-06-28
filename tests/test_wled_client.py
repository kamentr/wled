"""Unit tests for WLED client."""

import pytest
import responses
from unittest.mock import patch, Mock
from src.wled_client import WLEDClient


class TestWLEDClient:
    """Test cases for WLEDClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = WLEDClient('http://test.local')
        
    @responses.activate
    def test_get_state_success(self):
        """Test successful state retrieval."""
        mock_state = {'on': True, 'bri': 128}
        responses.add(
            responses.GET,
            'http://test.local/json/state',
            json=mock_state,
            status=200
        )
        
        result = self.client.get_state()
        assert result == mock_state
        
    @responses.activate
    def test_get_state_failure(self):
        """Test state retrieval failure."""
        responses.add(
            responses.GET,
            'http://test.local/json/state',
            status=500
        )
        
        result = self.client.get_state()
        assert result is None
        
    @responses.activate
    def test_get_effects_success(self):
        """Test successful effects retrieval."""
        mock_effects = ['Solid', 'Blink', 'Rainbow']
        responses.add(
            responses.GET,
            'http://test.local/json/effects',
            json={'effects': mock_effects},
            status=200
        )
        
        result = self.client.get_effects()
        assert result == mock_effects
        
    @responses.activate
    def test_get_effects_failure(self):
        """Test effects retrieval failure."""
        responses.add(
            responses.GET,
            'http://test.local/json/effects',
            status=500
        )
        
        result = self.client.get_effects()
        assert result is None
        
    @responses.activate
    def test_turn_on_success(self):
        """Test successful turn on."""
        responses.add(
            responses.POST,
            'http://test.local/json/state',
            json={'success': True},
            status=200
        )
        
        result = self.client.turn_on()
        assert result is True
        
    @responses.activate
    def test_turn_off_success(self):
        """Test successful turn off."""
        responses.add(
            responses.POST,
            'http://test.local/json/state',
            json={'success': True},
            status=200
        )
        
        result = self.client.turn_off()
        assert result is True
        
    @responses.activate
    def test_toggle_success(self):
        """Test successful toggle."""
        # Mock current state as off
        responses.add(
            responses.GET,
            'http://test.local/json/state',
            json={'on': False},
            status=200
        )
        
        # Mock toggle response
        responses.add(
            responses.POST,
            'http://test.local/json/state',
            json={'success': True},
            status=200
        )
        
        result = self.client.toggle()
        assert result is True
        
    @responses.activate
    def test_set_brightness_valid(self):
        """Test setting valid brightness."""
        responses.add(
            responses.POST,
            'http://test.local/json/state',
            json={'success': True},
            status=200
        )
        
        result = self.client.set_brightness(128)
        assert result is True
        
    def test_set_brightness_invalid(self):
        """Test setting invalid brightness."""
        result = self.client.set_brightness(300)
        assert result is False
        
        result = self.client.set_brightness(-1)
        assert result is False
        
    @responses.activate
    def test_set_color_valid(self):
        """Test setting valid color."""
        responses.add(
            responses.POST,
            'http://test.local/json/state',
            json={'success': True},
            status=200
        )
        
        result = self.client.set_color(255, 128, 64)
        assert result is True
        
    def test_set_color_invalid(self):
        """Test setting invalid color values."""
        result = self.client.set_color(300, 128, 64)
        assert result is False
        
        result = self.client.set_color(255, -1, 64)
        assert result is False
        
    @responses.activate
    def test_set_effect_valid(self):
        """Test setting valid effect."""
        responses.add(
            responses.POST,
            'http://test.local/json/state',
            json={'success': True},
            status=200
        )
        
        result = self.client.set_effect(5)
        assert result is True
        
    def test_set_effect_invalid(self):
        """Test setting invalid effect."""
        result = self.client.set_effect(200)
        assert result is False
        
        result = self.client.set_effect(-1)
        assert result is False
        
    @responses.activate
    def test_set_effect_speed_valid(self):
        """Test setting valid effect speed."""
        responses.add(
            responses.POST,
            'http://test.local/json/state',
            json={'success': True},
            status=200
        )
        
        result = self.client.set_effect_speed(128)
        assert result is True
        
    def test_set_effect_speed_invalid(self):
        """Test setting invalid effect speed."""
        result = self.client.set_effect_speed(300)
        assert result is False
        
    @responses.activate
    def test_set_effect_intensity_valid(self):
        """Test setting valid effect intensity."""
        responses.add(
            responses.POST,
            'http://test.local/json/state',
            json={'success': True},
            status=200
        )
        
        result = self.client.set_effect_intensity(128)
        assert result is True
        
    def test_set_effect_intensity_invalid(self):
        """Test setting invalid effect intensity."""
        result = self.client.set_effect_intensity(300)
        assert result is False
        
    @responses.activate
    def test_is_connected_true(self):
        """Test connection check when device is reachable."""
        responses.add(
            responses.GET,
            'http://test.local/json/state',
            json={'on': True},
            status=200
        )
        
        result = self.client.is_connected()
        assert result is True
        
    @responses.activate
    def test_is_connected_false(self):
        """Test connection check when device is not reachable."""
        responses.add(
            responses.GET,
            'http://test.local/json/state',
            status=500
        )
        
        result = self.client.is_connected()
        assert result is False 
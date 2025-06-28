# WLED Controller

A Python web application for controlling WLED lights with a modern, responsive web interface. This project provides a wrapper around the WLED JSON API with a beautiful web UI for easy control of your WLED devices.

## Features

- **Power Control**: Turn lights on/off with a single click
- **Brightness Control**: Adjust brightness with a smooth slider (0-255)
- **Color Control**: 
  - Color picker for intuitive color selection
  - RGBW input fields for precise control
  - Preset color buttons for quick access
- **Effects Control**: 
  - Dynamic loading of available WLED effects
  - Effect speed and intensity adjustment
  - Real-time effect application
- **Real-time Updates**: UI automatically syncs with WLED device state
- **Responsive Design**: Works on desktop and mobile devices
- **Connection Status**: Visual indicator of WLED device connectivity

## Prerequisites

- Python 3.8 or higher
- A WLED device accessible on your network
- Network connectivity to your WLED device

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd wled
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the project root to configure the application:

```env
# WLED device host (default: http://wled.local)
WLED_HOST=http://wled.local

# Web server configuration (optional)
HOST=127.0.0.1
PORT=8000
RELOAD=false
```

### Finding Your WLED Device

1. **Using mDNS** (recommended):
   - If your WLED device is named "wled", it should be accessible at `http://wled.local`
   - If your device has a different name, use `http://<device-name>.local`

2. **Using IP Address**:
   - Find your WLED device's IP address in your router's admin panel
   - Use the IP address: `http://192.168.1.100` (replace with actual IP)

3. **Using WLED App**:
   - Open the WLED app and check the device's IP address
   - Use that IP address in the configuration

## Usage

### Starting the Application

1. **Run the main application**:
   ```bash
   python main.py
   ```

2. **Access the web interface**:
   Open your browser and navigate to `http://127.0.0.1:8000`

### Using the Web Interface

1. **Power Control**:
   - Click the main power button to toggle lights on/off
   - Use the "Turn On" and "Turn Off" buttons for direct control

2. **Brightness Control**:
   - Drag the brightness slider to adjust brightness (0-255)
   - The current value is displayed next to the slider

3. **Color Control**:
   - Use the color picker for visual color selection
   - Enter precise RGBW values in the input fields
   - Click preset color buttons for quick access to common colors
   - Click "Set Color" to apply the selected color

4. **Effects Control**:
   - Select an effect from the dropdown menu
   - Adjust speed and intensity using the sliders
   - Click "Apply Effect" to apply all effect settings at once

### API Usage

The application also provides a REST API for programmatic control:

```python
import requests

# Get current state
response = requests.get('http://127.0.0.1:8000/api/state')
state = response.json()

# Turn lights on
requests.post('http://127.0.0.1:8000/api/power/on')

# Set color (red)
requests.post('http://127.0.0.1:8000/api/color', 
              json={'red': 255, 'green': 0, 'blue': 0})

# Set brightness
requests.post('http://127.0.0.1:8000/api/brightness', 
              json={'brightness': 128})

# Apply effect
requests.post('http://127.0.0.1:8000/api/effect', 
              json={'effect_id': 5})
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/state` | Get current WLED state |
| GET | `/api/effects` | Get available effects |
| GET | `/api/health` | Health check |
| POST | `/api/power` | Toggle power |
| POST | `/api/power/on` | Turn lights on |
| POST | `/api/power/off` | Turn lights off |
| POST | `/api/brightness` | Set brightness |
| POST | `/api/color` | Set color |
| POST | `/api/effect` | Set effect |
| POST | `/api/effect/speed` | Set effect speed |
| POST | `/api/effect/intensity` | Set effect intensity |

## Development

### Project Structure

```
wled/
├── src/
│   ├── __init__.py
│   ├── wled_client.py    # WLED API client
│   └── app.py           # FastAPI application
├── static/
│   └── app.js           # Frontend JavaScript
├── templates/
│   └── index.html       # Main web interface
├── tests/
│   ├── __init__.py
│   └── test_wled_client.py
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── .env                 # Environment configuration
└── README.md           # This file
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_wled_client.py
```

### Code Style

The project follows PEP 8 guidelines. Use the following tools for code quality:

```bash
# Format code with Black
black src/ tests/

# Check code style with flake8
flake8 src/ tests/

# Run type checking with mypy
mypy src/
```

## Troubleshooting

### Common Issues

1. **"WLED not reachable" error**:
   - Check that your WLED device is powered on and connected to the network
   - Verify the WLED_HOST setting in your `.env` file
   - Try using the IP address instead of the hostname
   - Check your firewall settings

2. **"Connection failed" error**:
   - Ensure your computer and WLED device are on the same network
   - Try pinging the WLED device to verify connectivity
   - Check if the WLED device is accessible via its web interface

3. **Effects not loading**:
   - Some WLED devices may not support the effects API
   - Check your WLED firmware version
   - Try accessing the effects directly via the WLED web interface

4. **Color not updating**:
   - Ensure the lights are turned on
   - Check that the WLED device supports the color format being sent
   - Verify the RGBW values are within the valid range (0-255)

### Debug Mode

Enable debug logging by setting the log level:

```python
# In src/app.py, change:
logging.basicConfig(level=logging.DEBUG)
```

### Network Diagnostics

Test connectivity to your WLED device:

```bash
# Test mDNS resolution
ping wled.local

# Test direct IP access (replace with your device's IP)
ping 192.168.1.100

# Test HTTP access
curl http://wled.local/json/state
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [WLED Project](https://github.com/Aircoookie/WLED) - The amazing WLED firmware
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for building APIs
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework

## Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Search existing issues on GitHub
3. Create a new issue with detailed information about your problem

For WLED-specific issues, refer to the [WLED documentation](https://kno.wled.ge/). 
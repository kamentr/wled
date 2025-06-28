// WLED Controller Frontend JavaScript

class WLEDController {
    constructor() {
        this.currentState = null;
        this.effects = [];
        this.effectNameToId = {};
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.initDarkMode();
        await this.checkConnection();
        await this.loadEffects();
        await this.loadCurrentState();
        this.startStatePolling();
    }

    initDarkMode() {
        // Check for saved theme preference or default to light mode
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            document.documentElement.classList.add('dark');
            this.updateDarkModeIcons(true);
        } else {
            document.documentElement.classList.remove('dark');
            this.updateDarkModeIcons(false);
        }
    }

    updateDarkModeIcons(isDark) {
        const sunIcon = document.getElementById('sun-icon');
        const moonIcon = document.getElementById('moon-icon');
        
        if (isDark) {
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        } else {
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        }
    }

    toggleDarkMode() {
        const isDark = document.documentElement.classList.contains('dark');
        
        if (isDark) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            this.updateDarkModeIcons(false);
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            this.updateDarkModeIcons(true);
        }
    }

    setupEventListeners() {
        // Dark mode toggle
        document.getElementById('dark-mode-toggle').addEventListener('click', () => this.toggleDarkMode());

        // Power controls
        document.getElementById('power-toggle').addEventListener('click', () => this.togglePower());
        document.getElementById('turn-on').addEventListener('click', () => this.turnOn());
        document.getElementById('turn-off').addEventListener('click', () => this.turnOff());

        // Brightness control
        const brightnessSlider = document.getElementById('brightness-slider');
        brightnessSlider.addEventListener('input', (e) => {
            document.getElementById('brightness-value').textContent = e.target.value;
        });
        brightnessSlider.addEventListener('change', (e) => this.setBrightness(e.target.value));

        // Color controls
        const colorPicker = document.getElementById('color-picker');
        colorPicker.addEventListener('change', (e) => this.updateColorFromPicker(e.target.value));
        colorPicker.addEventListener('input', (e) => this.updateColorFromPicker(e.target.value));

        // RGB inputs
        ['red-value', 'green-value', 'blue-value', 'white-value'].forEach(id => {
            document.getElementById(id).addEventListener('change', () => this.updateColorFromInputs());
        });

        // Set color button
        document.getElementById('set-color').addEventListener('click', () => this.setColor());

        // Preset colors
        document.querySelectorAll('.preset-color').forEach(button => {
            button.addEventListener('click', (e) => {
                const color = e.target.dataset.color;
                this.setPresetColor(color);
            });
        });

        // Effect search
        const effectSearch = document.getElementById('effect-search');
        effectSearch.addEventListener('input', (e) => this.filterEffects(e.target.value));
        effectSearch.addEventListener('keydown', (e) => this.handleEffectSearchKeydown(e));

        // Effect controls
        document.getElementById('effect-select').addEventListener('change', (e) => {
            if (e.target.value !== '') {
                this.setEffect(parseInt(e.target.value));
            }
        });

        // Effect speed and intensity
        const speedSlider = document.getElementById('speed-slider');
        speedSlider.addEventListener('input', (e) => {
            document.getElementById('speed-value').textContent = e.target.value;
        });
        speedSlider.addEventListener('change', (e) => this.setEffectSpeed(e.target.value));

        const intensitySlider = document.getElementById('intensity-slider');
        intensitySlider.addEventListener('input', (e) => {
            document.getElementById('intensity-value').textContent = e.target.value;
        });
        intensitySlider.addEventListener('change', (e) => this.setEffectIntensity(e.target.value));

        // Apply effect button
        document.getElementById('set-effect').addEventListener('click', () => this.applyEffect());
    }

    async checkConnection() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            const statusElement = document.getElementById('status-text');
            if (data.wled_connected) {
                statusElement.textContent = 'Connected to WLED';
                statusElement.className = 'px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
            } else {
                statusElement.textContent = 'WLED not reachable';
                statusElement.className = 'px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
            }
        } catch (error) {
            console.error('Connection check failed:', error);
            const statusElement = document.getElementById('status-text');
            statusElement.textContent = 'Connection failed';
            statusElement.className = 'px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
        }
    }

    async loadEffects() {
        try {
            const response = await fetch('/api/effects');
            const data = await response.json();
            this.effects = data.effects || [];
            
            // Update the effects dropdown with all effects
            this.updateEffectOptions(this.effects);
            
            // Update effects count
            this.updateEffectsCount(this.effects.length, this.effects.length);
            
        } catch (error) {
            console.error('Failed to load effects:', error);
            this.showStatus('Failed to load effects', 'error');
        }
    }

    async loadCurrentState() {
        try {
            const response = await fetch('/api/state');
            this.currentState = await response.json();
            this.updateUIFromState();
        } catch (error) {
            console.error('Failed to load current state:', error);
        }
    }

    updateUIFromState() {
        if (!this.currentState) return;

        // Update power button
        const powerButton = document.getElementById('power-toggle');
        if (this.currentState.on) {
            powerButton.textContent = 'Turn Off';
            powerButton.className = 'w-full py-3 px-4 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors';
        } else {
            powerButton.textContent = 'Turn On';
            powerButton.className = 'w-full py-3 px-4 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors';
        }

        // Update brightness
        if (this.currentState.bri !== undefined) {
            const brightnessSlider = document.getElementById('brightness-slider');
            const brightnessValue = document.getElementById('brightness-value');
            brightnessSlider.value = this.currentState.bri;
            brightnessValue.textContent = this.currentState.bri;
        }

        // Update color if segments exist
        if (this.currentState.seg && this.currentState.seg[0] && this.currentState.seg[0].col) {
            const color = this.currentState.seg[0].col[0];
            if (color && color.length >= 3) {
                const [r, g, b, w = 0] = color;
                this.updateColorInputs(r, g, b, w);
            }
        }

        // Update effect if segments exist
        if (this.currentState.seg && this.currentState.seg[0] && this.currentState.seg[0].fx !== undefined) {
            const effectSelect = document.getElementById('effect-select');
            effectSelect.value = this.currentState.seg[0].fx;
        }

        // Update effect speed and intensity
        if (this.currentState.seg && this.currentState.seg[0]) {
            const segment = this.currentState.seg[0];
            if (segment.sx !== undefined) {
                const speedSlider = document.getElementById('speed-slider');
                const speedValue = document.getElementById('speed-value');
                speedSlider.value = segment.sx;
                speedValue.textContent = segment.sx;
            }
            if (segment.ix !== undefined) {
                const intensitySlider = document.getElementById('intensity-slider');
                const intensityValue = document.getElementById('intensity-value');
                intensitySlider.value = segment.ix;
                intensityValue.textContent = segment.ix;
            }
        }
    }

    updateColorInputs(r, g, b, w = 0) {
        document.getElementById('red-value').value = r;
        document.getElementById('green-value').value = g;
        document.getElementById('blue-value').value = b;
        document.getElementById('white-value').value = w;
        
        // Update color picker
        const hexColor = this.rgbToHex(r, g, b);
        document.getElementById('color-picker').value = hexColor;
    }

    updateColorFromPicker(hexColor) {
        const rgb = this.hexToRgb(hexColor);
        if (rgb) {
            this.updateColorInputs(rgb.r, rgb.g, rgb.b);
        }
    }

    updateColorFromInputs() {
        const r = parseInt(document.getElementById('red-value').value) || 0;
        const g = parseInt(document.getElementById('green-value').value) || 0;
        const b = parseInt(document.getElementById('blue-value').value) || 0;
        const w = parseInt(document.getElementById('white-value').value) || 0;
        
        // Update color picker
        const hexColor = this.rgbToHex(r, g, b);
        document.getElementById('color-picker').value = hexColor;
    }

    setPresetColor(hexColor) {
        const rgb = this.hexToRgb(hexColor);
        if (rgb) {
            this.updateColorInputs(rgb.r, rgb.g, rgb.b);
            this.setColor();
        }
    }

    rgbToHex(r, g, b) {
        return '#' + [r, g, b].map(x => {
            const hex = x.toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        }).join('');
    }

    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    startStatePolling() {
        // Poll for state updates every 2 seconds
        setInterval(() => {
            this.loadCurrentState();
        }, 2000);
    }

    async makeRequest(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Request failed:', error);
            this.showStatus(`Request failed: ${error.message}`, 'error');
            throw error;
        }
    }

    showStatus(message, type = 'info') {
        const statusDiv = document.getElementById('status-message');
        const statusText = document.getElementById('status-text-content');
        
        statusText.textContent = message;
        
        // Remove existing classes
        statusDiv.className = 'mt-6';
        
        // Add appropriate styling
        if (type === 'error') {
            statusDiv.classList.add('bg-red-100', 'border', 'border-red-400', 'text-red-700', 'dark:bg-red-900', 'dark:border-red-700', 'dark:text-red-200', 'rounded-lg', 'p-4');
        } else if (type === 'success') {
            statusDiv.classList.add('bg-green-100', 'border', 'border-green-400', 'text-green-700', 'dark:bg-green-900', 'dark:border-green-700', 'dark:text-green-200', 'rounded-lg', 'p-4');
        } else {
            statusDiv.classList.add('bg-blue-100', 'border', 'border-blue-400', 'text-blue-700', 'dark:bg-blue-900', 'dark:border-blue-700', 'dark:text-blue-200', 'rounded-lg', 'p-4');
        }
        
        statusDiv.classList.remove('hidden');
        
        // Hide after 3 seconds
        setTimeout(() => {
            statusDiv.classList.add('hidden');
        }, 3000);
    }

    async togglePower() {
        try {
            await this.makeRequest('/api/power', { method: 'POST' });
            this.showStatus('Power toggled successfully', 'success');
            await this.loadCurrentState();
        } catch (error) {
            this.showStatus('Failed to toggle power', 'error');
        }
    }

    async turnOn() {
        try {
            await this.makeRequest('/api/power/on', { method: 'POST' });
            this.showStatus('Lights turned on', 'success');
            await this.loadCurrentState();
        } catch (error) {
            this.showStatus('Failed to turn on lights', 'error');
        }
    }

    async turnOff() {
        try {
            await this.makeRequest('/api/power/off', { method: 'POST' });
            this.showStatus('Lights turned off', 'success');
            await this.loadCurrentState();
        } catch (error) {
            this.showStatus('Failed to turn off lights', 'error');
        }
    }

    async setBrightness(brightness) {
        try {
            await this.makeRequest('/api/brightness', {
                method: 'POST',
                body: JSON.stringify({ brightness: parseInt(brightness) })
            });
            this.showStatus('Brightness updated', 'success');
        } catch (error) {
            this.showStatus('Failed to set brightness', 'error');
        }
    }

    async setColor() {
        const r = parseInt(document.getElementById('red-value').value) || 0;
        const g = parseInt(document.getElementById('green-value').value) || 0;
        const b = parseInt(document.getElementById('blue-value').value) || 0;
        const w = parseInt(document.getElementById('white-value').value) || 0;

        try {
            await this.makeRequest('/api/color', {
                method: 'POST',
                body: JSON.stringify({ red: r, green: g, blue: b, white: w })
            });
            this.showStatus('Color updated', 'success');
        } catch (error) {
            this.showStatus('Failed to set color', 'error');
        }
    }

    async setEffect(effectId) {
        try {
            await this.makeRequest('/api/effect', {
                method: 'POST',
                body: JSON.stringify({ effect_id: effectId })
            });
            this.showStatus('Effect applied', 'success');
        } catch (error) {
            this.showStatus('Failed to set effect', 'error');
        }
    }

    async setEffectSpeed(speed) {
        try {
            await this.makeRequest('/api/effect/speed', {
                method: 'POST',
                body: JSON.stringify({ speed: parseInt(speed) })
            });
            this.showStatus('Effect speed updated', 'success');
        } catch (error) {
            this.showStatus('Failed to set effect speed', 'error');
        }
    }

    async setEffectIntensity(intensity) {
        try {
            await this.makeRequest('/api/effect/intensity', {
                method: 'POST',
                body: JSON.stringify({ intensity: parseInt(intensity) })
            });
            this.showStatus('Effect intensity updated', 'success');
        } catch (error) {
            this.showStatus('Failed to set effect intensity', 'error');
        }
    }

    async applyEffect() {
        const effectSelect = document.getElementById('effect-select');
        const speedSlider = document.getElementById('speed-slider');
        const intensitySlider = document.getElementById('intensity-slider');

        if (effectSelect.value === '') {
            this.showStatus('Please select an effect first', 'error');
            return;
        }

        try {
            // Apply effect
            await this.setEffect(parseInt(effectSelect.value));
            
            // Apply speed and intensity
            await this.setEffectSpeed(speedSlider.value);
            await this.setEffectIntensity(intensitySlider.value);
            
            this.showStatus('Effect applied with settings', 'success');
        } catch (error) {
            this.showStatus('Failed to apply effect', 'error');
        }
    }

    filterEffects(query) {
        const filteredEffects = this.effects.filter(effect =>
            effect.name.toLowerCase().includes(query.toLowerCase())
        );
        this.updateEffectOptions(filteredEffects);
        this.updateEffectsCount(filteredEffects.length, this.effects.length);
    }

    handleEffectSearchKeydown(e) {
        if (e.key === 'ArrowDown') {
            const effectSelect = document.getElementById('effect-select');
            const selectedIndex = Array.from(effectSelect.options).findIndex(option => option.selected);
            const nextIndex = (selectedIndex + 1) % effectSelect.options.length;
            effectSelect.options[nextIndex].selected = true;
            e.preventDefault();
        } else if (e.key === 'ArrowUp') {
            const effectSelect = document.getElementById('effect-select');
            const selectedIndex = Array.from(effectSelect.options).findIndex(option => option.selected);
            const prevIndex = (selectedIndex - 1 + effectSelect.options.length) % effectSelect.options.length;
            effectSelect.options[prevIndex].selected = true;
            e.preventDefault();
        }
    }

    updateEffectOptions(effects) {
        const effectSelect = document.getElementById('effect-select');
        const currentValue = effectSelect.value; // Preserve current selection
        
        effectSelect.innerHTML = '<option value="">Select an effect...</option>';
        
        effects.forEach((effect) => {
            const option = document.createElement('option');
            option.value = effect.id; // Use the effect ID
            option.textContent = effect.name; // Use the effect name
            effectSelect.appendChild(option);
        });
        
        // Restore selection if it still exists in filtered results
        if (currentValue && effects.some(effect => effect.id == currentValue)) {
            effectSelect.value = currentValue;
        }
    }

    updateEffectsCount(visibleCount, totalCount) {
        const effectsCount = document.getElementById('effects-count');
        const visibleCountSpan = document.getElementById('visible-count');
        const totalCountSpan = document.getElementById('total-count');
        
        visibleCountSpan.textContent = visibleCount;
        totalCountSpan.textContent = totalCount;
        
        if (totalCount > 0) {
            effectsCount.classList.remove('hidden');
        } else {
            effectsCount.classList.add('hidden');
        }
    }
}

// Initialize the controller when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new WLEDController();
}); 
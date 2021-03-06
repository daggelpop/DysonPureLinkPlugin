# -*- coding: utf-8 -*-

"""Value types, enums and mappings package"""

# Map for connection return code and its meaning
CONNECTION_STATE = {
    0: 'Connection successful',
    1: 'Connection refused: incorrect protocol version',
    2: 'Connection refused: invalid client identifier',
    3: 'Connection refused: server unavailable',
    4: 'Connection refused: bad username or password',
    5: 'Connection refused: not authorised',
    99: 'Connection refused: timeout'
}

DISCONNECTION_STATE = {
    0: 'Disconnection successful',
    50: 'Disconnection error: unexpected error',
    99: 'Disconnection error: timeout'
}

class FanMode(object):
    """Enum for fan mode"""

    OFF = 'OFF'
    ON = 'FAN'
    AUTO = 'AUTO'

class StandbyMonitoring(object):
    """Enum for monitor air quality when on standby"""

    ON = 'ON'
    OFF = 'OFF'

"""Custom Errors"""

class ConnectionError(Exception):
    """Custom error to handle connect device issues"""

    def __init__(self, return_code, *args):
        super(ConnectionError, self).__init__(*args)
        self.message = CONNECTION_STATE[return_code]

class DisconnectionError(Exception):
    """Custom error to handle disconnect device issues"""
    def __init__(self, return_code, *args):
        super(DisconnectionError, self).__init__(*args)
        self.message = DISCONNECTION_STATE[return_code] if return_code in DISCONNECTION_STATE else DISCONNECTION_STATE[50]

class SensorsData(object):
    """Value type for sensors data"""

    def __init__(self, message, temperature_unit):
        data = message['data']
        humidity = data['hact']
        temperature = data['tact']
        volatile_compounds = data['vact']
        timer = data['sltm']
        self.temperature_unit = temperature_unit

        self.humidity = None if humidity == 'OFF' else int(humidity)
        if temperature == 'OFF':
            self.temperature = None
        else:
            conversion_function = self.kelvin_to_fahrenheit if temperature_unit == 'F' else self.kelvin_to_celsius
            self.temperature = conversion_function(float(temperature) / 10)
        self.volatile_compounds = 0 if volatile_compounds == 'INIT' else int(volatile_compounds)
        self.particles = int(data['pact'])
        self.timer = 0 if timer == 'OFF' else int(timer)

    def __repr__(self):
        """Return a String representation"""
        if self.has_data:
            return 'Temperature: {:.1f}°{}, Humidity: {} %, Humidex: {:.1f}, Volatile Compounds: {}, Particles: {}, Timer: {}'.format(
                self.temperature,
                self.temperature_unit,
                self.humidity,
                self.humidex,
                self.volatile_compounds,
                self.particles,
                self.timer,
            )
        else:
            return 'Volatile Compounds: {}, Particles: {}'.format(
                self.volatile_compounds,
                self.particles
            )

    @property
    def has_data(self):
        return self.temperature is not None or self.humidity is not None

    @staticmethod
    def is_sensors_data(message):
        return message['msg'] in ['ENVIRONMENTAL-CURRENT-SENSOR-DATA']

    @staticmethod
    def kelvin_to_fahrenheit(kelvin_value):
        return kelvin_value * 9 / 5 - 459.67

    @staticmethod
    def kelvin_to_celsius(kelvin_value):
        return kelvin_value - 273

    @staticmethod
    def fahrenheit_to_kelvin(fahrenheit_value):
        return (fahrenheit_value + 459.67) * 5 / 9

    @staticmethod
    def celsius_to_kelvin(celsius_value):
        return celsius_value + 273

    @property
    def humidex(self):
        return self.temperature + 0.5555 * \
                         (
                             6.112 * 10.0 ** (7.5 * (self.temperature / (237.7 + self.temperature)))
                             * (self.humidity / 100.0)
                             - 10
                         )


class StateData(object):
    """Value type for state data"""

    def __init__(self, message):
        data = message['product-state']

        self.fan_mode = self._get_field_value(data['fmod'])
        self.fan_speed = self._get_field_value(data['fnsp']).replace('AUTO', '-1')
        self.fan_state = self._get_field_value(data['fnst'])
        self.heating_mode = self._get_field_value(data['hmod'])
        self.heating_max_temp = self._get_field_value(data['hmax'])
        self.heating_state = self._get_field_value(data['hsta'])
        self.night_mode = self._get_field_value(data['nmod'])
        self.speed = self._get_field_value(data['fnsp'])
        self.oscillation = self._get_field_value(data['oson'])
        self.filter_life = self._get_field_value(data['filf'])
        self.quality_target = self._get_field_value(data['qtar'])
        self.standby_monitoring = self._get_field_value(data['rhtm'])

    def __repr__(self):
        """Return a String representation"""
        return 'Fan mode: {0}, Oscillation: {1}, Filter life: {2}, Standby monitoring: {3}'.format(
            self.fan_mode, self.oscillation, self.filter_life, self.standby_monitoring)

    @staticmethod
    def _get_field_value(field):
        """Get field value"""
        return field[-1] if isinstance(field, list) else field

    @staticmethod
    def is_state_data(message):
        return message['msg'] in ['CURRENT-STATE', 'STATE-CHANGE']

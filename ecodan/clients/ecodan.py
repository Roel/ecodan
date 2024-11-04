# Ecodan Modbus interface
# Copyright (C) 2023-2024  Roel Huybrechts

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass
import datetime
import minimalmodbus


@dataclass
class EcodanFloatData:
    value: float
    unit: str


@dataclass
class EcodanLutData:
    code: int
    description: str


@dataclass
class EcodanEnergyData:
    value: float
    unit: str
    date: datetime.date


class DummyEcodan:
    def __init__(self, *args, **kwargs):
        self.tank_target_temp = 0

    def get_tank_target_temp(self):
        value = self.tank_target_temp
        unit = '°C'
        return EcodanFloatData(value, unit)

    def set_tank_target_temp(self, value):
        if type(value) not in (int, float):
            raise TypeError("Value must be numeric.")

        if value < 10 or value > 60:
            raise ValueError("Value must be between 10 and 60 (inclusive).")

        print(f'Setting target temp to {value}')
        self.tank_target_temp = value

    def get_tank_temp(self):
        value = 42
        unit = '°C'
        return EcodanFloatData(value, unit)

    def get_house_temp(self):
        value = 22.5
        unit = '°C'
        return EcodanFloatData(value, unit)

    def get_house_target_temp(self):
        value = 21
        unit = '°C'
        return EcodanFloatData(value, unit)

    def get_outdoor_temp(self):
        value = 14.5
        unit = '°C'
        return EcodanFloatData(value, unit)

    def get_pump_freq(self):
        value = 38
        unit = 'Hz'
        return EcodanFloatData(value, unit)

    def get_flow(self):
        value = 19
        unit = 'l/min'
        return EcodanFloatData(value, unit)

    def get_pump_supply_temp(self):
        value = 50
        unit = '°C'
        return EcodanFloatData(value, unit)

    def get_pump_return_temp(self):
        value = 45
        unit = '°C'
        return EcodanFloatData(value, unit)

    def get_energy_consumed_tank(self):
        kwh_part = 3
        wh_part = 260
        value = kwh_part + (wh_part/1000)
        unit = 'kWh'

        year = 2023
        month = 9
        day = 1
        date = datetime.date(year, month, day)

        return EcodanEnergyData(value, unit, date)

    def get_energy_consumed_house(self):
        kwh_part = 3
        wh_part = 170
        value = kwh_part + (wh_part/1000)
        unit = 'kWh'

        year = 2023
        month = 9
        day = 1
        date = datetime.date(year, month, day)

        return EcodanEnergyData(value, unit, date)

    def get_energy_produced_tank(self):
        kwh_part = 9
        wh_part = 560
        value = kwh_part + (wh_part/1000)
        unit = 'kWh'

        year = 2023
        month = 9
        day = 1
        date = datetime.date(year, month, day)

        return EcodanEnergyData(value, unit, date)

    def get_energy_produced_house(self):
        kwh_part = 0
        wh_part = 180
        value = kwh_part + (wh_part/1000)
        unit = 'kWh'

        year = 2023
        month = 9
        day = 1
        date = datetime.date(year, month, day)

        return EcodanEnergyData(value, unit, date)


class Ecodan(minimalmodbus.Instrument):
    def __init__(self, port, slave=1, baudrate=9600, *args, **kwargs):
        super().__init__(port, slave, *args, **kwargs)
        self.serial.baudrate = baudrate

    def get_tank_target_temp(self):
        value = self.read_register(31, 2)
        unit = '°C'
        return EcodanFloatData(value, unit)

    def set_tank_target_temp(self, value):
        if type(value) not in (int, float):
            raise TypeError("Value must be numeric.")

        if value < 10 or value > 60:
            raise ValueError("Value must be between 10 and 60 (inclusive).")

        self.write_register(31, value, 2)

    def get_tank_temp(self):
        value = self.read_register(106, 2)
        unit = '°C'
        return EcodanFloatData(value, unit)

    def get_house_temp(self):
        value = self.read_register(94, 2)
        unit = '°C'
        return EcodanFloatData(value, unit)

    def get_house_target_temp(self):
        value = self.read_register(55, 2)
        unit = '°C'
        return EcodanFloatData(value, unit)

    def set_house_target_temp(self, value):
        if type(value) not in (int, float):
            raise TypeError("Value must be numeric.")

        if value < 5 or value > 25:
            raise ValueError("Value must be between 5 and 25 (inclusive).")

        self.write_register(55, value, 2)

    def get_outdoor_temp(self):
        value = self.read_register(99, 1, signed=True)
        unit = '°C'
        return EcodanFloatData(value, unit)

    def get_pump_freq(self):
        value = self.read_register(73)
        unit = 'Hz'
        return EcodanFloatData(value, unit)

    def get_flow(self):
        value = self.read_register(299)
        unit = 'l/min'
        return EcodanFloatData(value, unit)

    def get_pump_supply_temp(self):
        value = self.read_register(102, 2)
        unit = '°C'
        return EcodanFloatData(value, unit)

    def get_pump_return_temp(self):
        value = self.read_register(104, 2)
        unit = '°C'
        return EcodanFloatData(value, unit)

    def get_energy_consumed_tank(self):
        kwh_part = self.read_register(286)
        wh_part = self.read_register(287) * 10
        value = kwh_part + (wh_part/1000)
        unit = 'kWh'

        year = 2000 + self.read_register(279)
        month = self.read_register(280)
        day = self.read_register(281)
        date = datetime.date(year, month, day)

        return EcodanEnergyData(value, unit, date)

    def get_energy_consumed_house(self):
        kwh_part = self.read_register(282)
        wh_part = self.read_register(283) * 10
        value = kwh_part + (wh_part/1000)
        unit = 'kWh'

        year = 2000 + self.read_register(279)
        month = self.read_register(280)
        day = self.read_register(281)
        date = datetime.date(year, month, day)

        return EcodanEnergyData(value, unit, date)

    def get_energy_produced_tank(self):
        kwh_part = self.read_register(296)
        wh_part = self.read_register(297) * 10
        value = kwh_part + (wh_part/1000)
        unit = 'kWh'

        year = 2000 + self.read_register(289)
        month = self.read_register(290)
        day = self.read_register(291)
        date = datetime.date(year, month, day)

        return EcodanEnergyData(value, unit, date)

    def get_energy_produced_house(self):
        kwh_part = self.read_register(292)
        wh_part = self.read_register(293) * 10
        value = kwh_part + (wh_part/1000)
        unit = 'kWh'

        year = 2000 + self.read_register(289)
        month = self.read_register(290)
        day = self.read_register(291)
        date = datetime.date(year, month, day)

        return EcodanEnergyData(value, unit, date)

    def get_operating_mode(self):
        mode = self.read_register(26)

        operating_modes = {
            0: 'Stop',
            1: 'Hot water',
            2: 'Heating',
            3: 'Cooling',
            4: 'No voltage contact input (hot water storage)',
            5: 'Freeze stat',
            6: 'Legionella',
            7: 'Heating eco',
            8: 'Mode 1',
            9: 'Mode 2',
            10: 'Mode 3',
            11: 'No voltage contact input (heating up)'
        }

        return EcodanLutData(
            code=mode,
            description=operating_modes.get(mode, 'Unknown')
        )

    def get_heat_source(self):
        heat_source = self.read_register(80)

        heat_sources = {
            0: 'Heatpump',
            1: 'Immersion heater',
            2: 'Backup heater',
            3: 'Immersion and backup heater',
            4: 'Boiler'
        }

        return EcodanLutData(
            code=heat_source,
            description=heat_sources.get(heat_source, 'Unknown')
        )

    def get_defrost_status(self):
        defrost_status = self.read_register(67)

        defrost_statuses = {
            0: 'Normal',
            1: 'Standby',
            2: 'Defrost',
            3: 'Waiting restart'
        }

        return EcodanLutData(
            code=defrost_status,
            description=defrost_statuses.get(defrost_status, 'Unknown')
        )

    def get_dhw_enabled(self):
        dhw_enabled = self.read_register(39)

        dhw_status = {
            0: 'Enabled',
            1: 'Disabled'
        }

        return EcodanLutData(
            code=dhw_enabled,
            description=dhw_status.get(dhw_enabled, 'Unknown')
        )

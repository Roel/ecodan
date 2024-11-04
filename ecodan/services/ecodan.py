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

from clients.ecodan import Ecodan, EcodanFloatData, EcodanEnergyData, EcodanLutData


@dataclass
class EcodanDataDto:
    timestamp: datetime
    tank_temp: EcodanFloatData
    tank_target_temp: EcodanFloatData
    house_temp: EcodanFloatData
    house_target_temp: EcodanFloatData
    outdoor_temp: EcodanFloatData
    pump_freq: EcodanFloatData
    flow: EcodanFloatData
    pump_supply_temp: EcodanFloatData
    pump_return_temp: EcodanFloatData
    energy_consumed_tank: EcodanEnergyData
    energy_produced_tank: EcodanEnergyData
    energy_consumed_house: EcodanEnergyData
    energy_produced_house: EcodanEnergyData
    operating_mode: EcodanLutData
    heat_source: EcodanLutData
    defrost_status: EcodanLutData
    dhw_enabled: EcodanLutData


class EcodanService:
    def __init__(self, app):
        self.app = app

        self.client = Ecodan(
            port=self.app.config['ECODAN_SERIAL_PORT'],
            slave=self.app.config['ECODAN_SLAVE_ADDRESS'],
            baudrate=self.app.config['ECODAN_SERIAL_BAUDRATE']
        )

        self.__scheduled_jobs()

    def __scheduled_jobs(self):
        self.app.scheduler.add_job(
            self.read_data_to_influx, 'cron', second='0,30')

    async def read_data_to_influx(self):
        data = EcodanDataDto(
            timestamp=datetime.datetime.now(),
            tank_temp=self.client.get_tank_temp(),
            tank_target_temp=self.client.get_tank_target_temp(),
            house_temp=self.client.get_house_temp(),
            house_target_temp=self.client.get_house_target_temp(),
            outdoor_temp=self.client.get_outdoor_temp(),
            pump_freq=self.client.get_pump_freq(),
            flow=self.client.get_flow(),
            pump_supply_temp=self.client.get_pump_supply_temp(),
            pump_return_temp=self.client.get_pump_return_temp(),
            energy_consumed_house=self.client.get_energy_consumed_house(),
            energy_produced_house=self.client.get_energy_produced_house(),
            energy_consumed_tank=self.client.get_energy_consumed_tank(),
            energy_produced_tank=self.client.get_energy_produced_tank(),
            operating_mode=self.client.get_operating_mode(),
            heat_source=self.client.get_heat_source(),
            defrost_status=self.client.get_defrost_status(),
            dhw_enabled=self.client.get_dhw_enabled()
        )

        await self.app.services.influx.save_ecodan_data(data)

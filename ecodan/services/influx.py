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

import datetime
from db.models.energy_influx_state import EnergyInfluxState
from clients.influx import InfluxClient
from clients.ecodan import EcodanFloatData


class InfluxService:
    def __init__(self, app):
        self.app = app

        self.client = InfluxClient(
            host=self.app.config['INFLUX_HOST'],
            database=self.app.config['INFLUX_DATABASE'],
            username=self.app.config['INFLUX_USERNAME'],
            password=self.app.config['INFLUX_PASSWORD']
        )

    async def save_ecodan_data(self, ecodan_data):
        data = []

        mapping = {
            'ecodan2_tank_set_temp': ecodan_data.tank_target_temp,
            'ecodan2_tank_temp': ecodan_data.tank_temp,
            'ecodan2_house_set_temp': ecodan_data.house_target_temp,
            'ecodan2_house_temp': ecodan_data.house_temp,
            'ecodan2_outdoor_temp': ecodan_data.outdoor_temp,
            'ecodan2_pump_freq': ecodan_data.pump_freq,
            'ecodan2_flow': ecodan_data.flow,
            'ecodan2_t_flow': ecodan_data.pump_supply_temp,
            'ecodan2_t_return': ecodan_data.pump_return_temp
        }

        if ecodan_data.flow.value > 0:
            dt = ecodan_data.pump_supply_temp.value - ecodan_data.pump_return_temp.value
            flow_l_sec = ecodan_data.flow.value / 60
            thermal_output_power = EcodanFloatData(
                value=(dt * flow_l_sec * 4.2)*1000,
                unit='W'
            )
            mapping['ecodan2_thermal_output_power'] = thermal_output_power

        for stream, datapoint in mapping.items():
            data.append({
                'time': int(ecodan_data.timestamp.strftime('%s')) * 10**9,
                'measurement': stream,
                'fields': {
                    'value': datapoint.value * 1.0
                },
                'tags': {
                    'unit': datapoint.unit
                }
            })

        mapping_lut = {
            'ecodan2_operating_mode': ecodan_data.operating_mode,
            'ecodan2_heat_source': ecodan_data.heat_source,
            'ecodan2_defrost_status': ecodan_data.defrost_status,
            'ecodan2_dhw_enabled': ecodan_data.dhw_enabled
        }

        for stream, datapoint in mapping_lut.items():
            data.append({
                'time': int(ecodan_data.timestamp.strftime('%s')) * 10**9,
                'measurement': stream,
                'fields': {
                    'value': datapoint.code
                },
                'tags': {
                    'description': datapoint.description
                }
            })

        mapping_energy = {
            'ecodan2_nrg_cons_house': ecodan_data.energy_consumed_house,
            'ecodan2_nrg_cons_tank': ecodan_data.energy_consumed_tank,
            'ecodan2_nrg_prod_house': ecodan_data.energy_produced_house,
            'ecodan2_nrg_prod_tank': ecodan_data.energy_produced_tank,
        }

        for stream, datapoint in mapping_energy.items():
            current_state = await EnergyInfluxState.from_stream(stream)

            if current_state:
                updated = await current_state.update_from_ecodan(datapoint)
            else:
                current_state = EnergyInfluxState(
                    stream, datapoint.date, datapoint.value)
                await current_state.save()
                updated = True

            if updated:
                timestamp = datetime.datetime(
                    datapoint.date.year,
                    datapoint.date.month,
                    datapoint.date.day,
                    ecodan_data.timestamp.hour,
                    ecodan_data.timestamp.minute,
                    ecodan_data.timestamp.second)

                data.append({
                    'time': int(timestamp.strftime('%s')) * 10**9,
                    'measurement': stream,
                    'fields': {
                        'value': datapoint.value
                    },
                    'tags': {
                        'unit': datapoint.unit
                    }
                })

        self.client.write_points(data)

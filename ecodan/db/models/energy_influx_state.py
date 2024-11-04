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

from db.base import Model


class EnergyInfluxState(Model):
    def __init__(self, stream, last_date, last_value):
        self.stream = stream
        self.last_date = last_date
        self.last_value = last_value

    @staticmethod
    async def from_stream(stream):
        async with Model.db.connect() as conn:
            async with conn.execute(
                    'SELECT * FROM energy_influx_state WHERE stream = ?', (stream,)) as curs:
                result = await curs.fetchone()
                if result:
                    return EnergyInfluxState(*result)

    def data(self):
        return {
            'stream': self.stream,
            'last_date': self.last_date,
            'last_value': self.last_value
        }

    async def save(self):
        async with self.db.connect() as conn:
            await conn.execute(
                """INSERT INTO energy_influx_state VALUES (:stream, :last_date, :last_value)
                ON CONFLICT (stream) DO UPDATE SET
                    last_date = excluded.last_date,
                    last_value = excluded.last_value
                """, self.data())
            await conn.commit()

    async def update_from_ecodan(self, ecodan_data):
        if ecodan_data.date < self.last_date:
            return False

        if ecodan_data.date == self.last_date and ecodan_data.value <= self.last_value:
            return False

        self.last_date = ecodan_data.date
        self.last_value = ecodan_data.value
        await self.save()
        return True

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

from influxdb import InfluxDBClient


class DummyInfluxClient:
    def __init__(*args, **kwargs):
        pass

    def write_points(self, data):
        print(data)


class InfluxClient(InfluxDBClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

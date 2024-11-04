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

from quart import Blueprint, request, current_app as app
from quart_auth import basic_auth_required

api = Blueprint('api', __name__)


@api.put("/tank/target_temp")
@basic_auth_required()
async def set_tank_target_temp():
    data = await request.get_json()

    try:
        app.services.ecodan.client.set_tank_target_temp(data['value'])
    except (ValueError, TypeError, KeyError) as e:
        return {
            'status': 'error',
            'message': str(e)
        }, 400
    else:
        return {
            'status': 'ok'
        }


@api.put("/house/target_temp")
@basic_auth_required()
async def set_house_target_temp():
    data = await request.get_json()

    try:
        app.services.ecodan.client.set_house_target_temp(data['value'])
    except (ValueError, TypeError, KeyError) as e:
        return {
            'status': 'error',
            'message': str(e)
        }, 400
    else:
        return {
            'status': 'ok'
        }

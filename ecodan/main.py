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

import asyncio

from quart import Quart
from quart_auth import QuartAuth

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import Config
from db.base import Database
from services.ecodan import EcodanService
from services.influx import InfluxService

from blueprints.api import api
from blueprints.status import status


class Services:
    def __init__(self, app):
        self.app = app

        self.influx = InfluxService(self.app)
        self.ecodan = EcodanService(self.app)


app = Quart(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

app.db = Database(app)
app.auth = QuartAuth(app)


@app.before_serving
async def startup():
    await app.db.migrate()

    loop = asyncio.get_event_loop()

    app.scheduler = AsyncIOScheduler(event_loop=loop)
    app.scheduler.start()

    app.services = Services(app)

    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(status, url_prefix='/status')


@app.after_serving
async def shutdown():
    app.scheduler.shutdown()

from fastapi import FastAPI
import os
import asyncio
import prometheus_client
import traceback
import re
from prometheus_client import make_asgi_app, Gauge
from miio import DeviceFactory
from loguru import logger

prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

app = FastAPI(debug=False)
metrics_app = make_asgi_app()

class BackgroundRunner:
    def __init__(self, location, device_ip, device_token):
        self.location = location
        self.device_ip = device_ip
        self.device_token = device_token
        self.device = self.connect_device()
        self.device_model = location + self.device.info().model
        self.dev_metrics = re.sub('[^0-9a-zA-Z]+', '_', self.device_model).lower()
        self.temperature_gauge = Gauge('{dev_metrics}_temperature'.format(dev_metrics=self.dev_metrics), 'Temperature of {dev_model}'.format(dev_model=self.device_model))
        self.humidity_gauge = Gauge('{dev_metrics}_humidity'.format(dev_metrics=self.dev_metrics), 'Humidity of {dev_model}'.format(dev_model=self.device_model))
        self.aqi_gauge = Gauge('{dev_metrics}_aqi'.format(dev_metrics=self.dev_metrics), 'Aqi of {dev_model}'.format(dev_model=self.device_model))

    def connect_device(self):
        return DeviceFactory.create(self.device_ip, self.device_token)
    
    async def run_main(self):
        while True:
            try:
                self.temperature_gauge.set(self.device.status().temperature)
                self.humidity_gauge.set(self.device.status().humidity)
                self.aqi_gauge.set(self.device.status().aqi)
            except:
                logger.error(traceback.format_exc())
                self.device = self.connect_device()
            await asyncio.sleep(30)


@app.on_event('startup')
async def app_startup():
    try:
        runner = BackgroundRunner('', os.environ.get('device_ip', ''), os.environ.get('device_token', ''))
        asyncio.create_task(runner.run_main())
    except:
        exit()

app.mount("/metrics", metrics_app)
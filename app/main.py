from fastapi import FastAPI
import os
import asyncio
import prometheus_client
from prometheus_client import make_asgi_app, Gauge
from miio import DeviceFactory

prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

app = FastAPI(debug=False)
metrics_app = make_asgi_app()

class BackgroundRunner:
    def __init__(self, device, temperature_gauge, humidity_gauge, aqi_gauge):
        self.device = device
        self.temperature_gauge = temperature_gauge
        self.humidity_gauge = humidity_gauge
        self.aqi_gauge = aqi_gauge

    async def run_main(self):
        while True:
            self.temperature_gauge.set(self.device.status().temperature)
            self.humidity_gauge.set(self.device.status().humidity)
            self.aqi_gauge.set(self.device.status().aqi)
            await asyncio.sleep(30)

@app.on_event('startup')
async def app_startup():
    try:
        dev = DeviceFactory.create(os.environ.get('device_ip', ''), os.environ.get('device_token', ''))
        dev_model = dev.info().model
        tem = Gauge('miio_temperature_gauge', 'Temperature of {dev_model}'.format(dev_model=dev_model))
        hum = Gauge('miio_humidity_gauge', 'Humidity of {dev_model}'.format(dev_model=dev_model))
        aqi = Gauge('miio_aqi_gauge', 'Aqi of {dev_model}'.format(dev_model=dev_model))

        runner = BackgroundRunner(dev, tem, hum, aqi)
        asyncio.create_task(runner.run_main())
    except:
        exit()

app.mount("/metrics", metrics_app)
from flask import Flask
import os

from .assets import assets
from .settings import DevConfig, ProdConfig, TestConfig


app = Flask(__name__)
env = os.environ.get('CRONOS_ENV')
if env == 'dev':
    app.config.from_object(DevConfig)
elif env == 'test':
    app.config.from_object(TestConfig)
else:
    app.config.from_object(ProdConfig)
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('cronos startup')

assets.init_app(app)

from . import views

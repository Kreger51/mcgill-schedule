import os


class Config(object):
    WTF_CSRF_ENABLED = True
    CSRF_ENABLED = True
    SECRET_KEY = '0d7133fc-6831-4a4b-94d5-fb0cd3cf8a03'
    ASSETS_DEBUG = False


class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = False


class DevConfig(Config):
    """Development configuration."""
    ENV = 'dev'
    DEBUG = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets


class TestConfig(Config):
    TESTING = True
    DEBUG = True


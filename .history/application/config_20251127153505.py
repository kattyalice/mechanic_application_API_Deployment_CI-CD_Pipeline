import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Simelia5!4@localhost/mechanic_project'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-change-me")

    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    
class TestingConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///testing.db"
    TESTING = True
    DEBUG = True
    
    SECRET_KEY = "test-secret-key"
    
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    
class ProcutionConfig:
    SQLALCHEMY_DATABASE_URI = ''
    CACHE_TYPE = "SimpleCache"
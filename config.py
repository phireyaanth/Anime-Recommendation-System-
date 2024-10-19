# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///anime_users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

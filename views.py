from flask import Flask, request
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from utils import load_template

def index():
    return load_template('index.html')
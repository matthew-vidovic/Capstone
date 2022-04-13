import RPi.GPIO as GPIO    
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import serial
from time import sleep
from datetime import datetime

#import bluetooth
ser = serial.Serial('/dev/rfcomm0',9600)

while True:
    serialdata = ser.readline()
    print(serialdata.decode())
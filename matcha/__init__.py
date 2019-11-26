from flask import Flask
from flask_socketio import SocketIO
from matcha.models import DB

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET'

# Set up the socket
socket = SocketIO(app)

# Set up the database
db = DB()

from matcha import routes
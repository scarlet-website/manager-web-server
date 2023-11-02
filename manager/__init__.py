from uuid import uuid4

from flask_cors import CORS
from flask import Flask

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = str(uuid4())

from manager import routes

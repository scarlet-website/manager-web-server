from uuid import uuid4

from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = str(uuid4())

from manager import routes

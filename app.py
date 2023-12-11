import os
import sys
from manager import app

if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(__file__))
    app.run(debug=bool(os.getenv("DEBUG_MODE", default=False)))

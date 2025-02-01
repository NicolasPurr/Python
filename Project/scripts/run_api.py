import uvicorn
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from drugbank.api import *

# Task 15
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
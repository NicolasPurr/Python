import uvicorn
from drugbank.api import app

# Task 15
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
"""
Root-level main.py for Cloud Run deployment
This tells Cloud Run how to start the FastAPI app
"""

from riskportalai.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
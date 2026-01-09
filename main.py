"""
Entry point for Carbon Accounting API
Run with: python main.py
Or: uvicorn main:app --reload
"""

from carbon_api.app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
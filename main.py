from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict-chart")
async def predict_chart(file: UploadFile = File(...), model_type: str = Form("random_walk")):
    contents = await file.read()
    file_bytes = np.asarray(bytearray(contents), dtype=np.uint8)
    opencv_image = cv2.imdecode(file_bytes, 1)
    
    if opencv_image is None:
        return {"status": "error", "message": "Invalid image file uploaded."}
    
    hsv = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    if np.count_nonzero(mask) < 50:
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        mask = cv2.Canny(gray, 50, 150)
        
    height, width = mask.shape
    x_coords, y_coords = [], []
    
    for x in range(0, width, max(1, width // 150)):
        col = mask[:, x]
        indices = np.where(col > 0)[0]
        if len(indices) > 0:
            y_coords.append(height - np.min(indices))
            x_coords.append(x)
            
    if len(y_coords) > 5:
        y_min, y_max = min(y_coords), max(y_coords)
        if y_max == y_min: y_max += 1
        prices = 330 + (np.array(y_coords, dtype=float) - y_min) / (y_max - y_min) * 500
        
        # Calculate Simple Moving Average (SMA)
        window_size = 5
        sma = np.convolve(prices, np.ones(window_size)/window_size, mode='valid').tolist()
        
        future_steps = 30
        last_price = prices[-1]
        
        if model_type == "linear":
            # Linear Trend Extrapolation
            x_vals = np.arange(len(prices))
            slope, intercept = np.polyfit(x_vals, prices, 1)
            future_x = np.arange(len(prices), len(prices) + future_steps)
            future_prices = slope * future_x + intercept
        elif model_type == "exponential":
            # Exponential Smoothing Growth
            growth_factor = 1.01
            future_prices = [last_price * (growth_factor ** i) for i in range(1, future_steps + 1)]
            future_prices = np.array(future_prices)
        else:
            # Random Walk Simulation
            future_prices = last_price + np.cumsum(np.random.normal(1.2, 4.0, future_steps))
        
        return {
            "status": "success",
            "historical_prices": prices.tolist(),
            "sma": sma,
            "predicted_prices": future_prices.tolist()
        }
    
    return {"status": "error", "message": "Could not isolate chart line."}
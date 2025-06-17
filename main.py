import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
from train_model import train_models  # Import model training function
from visualization import visualize_stock  # Import stock visualization function
from data_processing import preprocess_data  # Import preprocessing function

# Step 1️⃣: Load and Preprocess Data
file_path = "C:/Users/Public/stockvolatilitydetector/processed_data.csv"
df = preprocess_data(file_path)  # Calls preprocessing function

# Step 2️⃣: Run Model Training
train_models(df)  # Calls training function from train_model.py

# Step 3️⃣: Visualize Results
visualize_stock(df)  # Calls visualization function from visualization.py

# Step 4️⃣: Print Final Evaluation Results
print("\n✅ Stock Market Volatility Detector Execution Completed!")
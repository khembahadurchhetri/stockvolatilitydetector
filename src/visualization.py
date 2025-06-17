import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt

# Step 1️⃣: Load Processed Data
file_path = "C:/Users/Public/stockvolatilitydetector/processed_data.csv"
df = pd.read_csv(file_path)

# Step 2️⃣: Convert Date Column to Proper Datetime Format
df.loc[:, "Date"] = pd.to_datetime(df["Date"])  # Ensure proper datetime formatting
df.set_index("Date", inplace=True)  # Set Date as the index
df.index = pd.to_datetime(df.index)  # Ensure index is DatetimeIndex

# Step 3️⃣: Check if Data Is Loaded Correctly
print("\n🔍 First 5 Rows of Data:")
print(df.head())

# Step 4️⃣: Generate Candlestick Chart Using mplfinance
ohlc_data = df[["Open", "High", "Low", "Close", "Volume"]]

mpf.plot(
    ohlc_data.tail(50),  # Show last 50 days
    type="candle",
    volume=True,
    style="charles",
    title="Stock Price Movements",
    ylabel="Stock Price",
    ylabel_lower="Volume"
)

# Step 5️⃣: Visualize Rolling Standard Deviation
window_size = 14
rolling_std = np.std(np.lib.stride_tricks.sliding_window_view(df["Close"], window_size), axis=1)

# Align with original dataframe index
df = df.iloc[window_size - 1:].copy()
df["Rolling_Std_NumPy"] = rolling_std

# Plot Rolling Standard Deviation Distribution
plt.figure(figsize=(10, 5))
plt.hist(df["Rolling_Std_NumPy"], bins=30, alpha=0.7, color="blue")
plt.title("Distribution of Rolling Standard Deviation (NumPy)")
plt.xlabel("Volatility")
plt.ylabel("Frequency")
plt.grid()

# Step 6️⃣: Ensure Visualization Appears
plt.show()
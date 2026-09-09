import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Load stock volatility data
file_path = "C:/Users/Public/AI stock model/high_volatility_days.csv"  # Update path if needed
df = pd.read_csv(file_path)

# Handle missing values
df.dropna(inplace=True)

# Normalize numeric features
scaler = MinMaxScaler()
df[["Open", "High", "Low", "Close", "Volume", "Rolling_Std"]] = scaler.fit_transform(
    df[["Open", "High", "Low", "Close", "Volume", "Rolling_Std"]]
)

# Convert Date column to datetime format
df["Date"] = pd.to_datetime(df["Date"])
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# Save processed data
df.to_csv("C:/Users/Public/stockvolatilitydetector/processed_data.csv", index=False)

print("✅ Data preprocessing completed! Saved as processed_data.csv.")
df.to_csv("C:/Users/Public/stockvolatilitydetector/processed_data.csv", index=False)
print("✅ Data preprocessing completed! Saved as processed_data.csv.")
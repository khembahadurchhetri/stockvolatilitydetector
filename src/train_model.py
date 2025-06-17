import pandas as pd
import numpy as np
import mplfinance as mpf
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt

# Step 1️⃣: Load Processed Data
file_path = "C:/Users/Public/stockvolatilitydetector/processed_data.csv"
df = pd.read_csv(file_path)

# Step 2️⃣: Feature Engineering - Adding Technical Indicators
df["RSI"] = 100 - (100 / (1 + df["Close"].pct_change().rolling(window=14).mean()))  # Relative Strength Index
df["MACD"] = df["Close"].ewm(span=12).mean() - df["Close"].ewm(span=26).mean()  # Moving Average Convergence Divergence
df["ATR"] = (df["High"] - df["Low"]).rolling(window=14).mean()  # Average True Range

# Step 3️⃣: Implement Rolling Standard Deviation Using NumPy Sliding Window
window_size = 14
rolling_std = np.std(np.lib.stride_tricks.sliding_window_view(df["Close"], window_size), axis=1)

# Align with original dataframe index
df = df.iloc[window_size - 1:].copy()
df["Rolling_Std_NumPy"] = rolling_std

# Step 4️⃣: Refine Features & Target Variable
X = df[["Close", "Volume", "RSI", "MACD", "ATR"]]  # Removed Bollinger Bands
y = (df["Rolling_Std_NumPy"] > df["Rolling_Std_NumPy"].quantile(0.75)).astype(int)  # Top 25% high-volatility days

# Step 5️⃣: Verify Label Distribution
print("\n🔍 Label Distribution Before Balancing:")
print(y.value_counts())

# Handle missing values caused by rolling calculations
X = X.dropna().copy()
y = y.loc[X.index]  # Match indices after NaN removal

# Step 6️⃣: Apply SMOTE to Balance Classes
smote = SMOTE(sampling_strategy=0.75, random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# Verify label distribution after SMOTE
print("\n🔍 Label Distribution After Balancing:")
print(y_resampled.value_counts())

# Step 7️⃣: Visualize Data Distribution
plt.hist(df["Rolling_Std_NumPy"], bins=30)
plt.title("Distribution of Rolling Standard Deviation (NumPy)")
plt.show()

# Step 8️⃣: Generate Candlestick Chart Using mplfinance
ohlc_data = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
ohlc_data.loc[:, "Date"] = pd.to_datetime(ohlc_data["Date"])  # Convert Date column
ohlc_data.set_index("Date", inplace=True)  # Set Date as proper index
ohlc_data.index = pd.to_datetime(ohlc_data.index)  # Ensure index is DatetimeIndex

mpf.plot(
    ohlc_data.tail(50),  # Show last 50 days
    type="candle",
    volume=True,
    style="charles",
    title="Stock Price Movements",
    ylabel="Stock Price",
    ylabel_lower="Volume"
)

# Step 9️⃣: Split Data for Training and Testing
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.3, random_state=42)

# Step 🔟: Train Optimized Models
model_rf = RandomForestClassifier(n_estimators=5, max_depth=1, random_state=42)
model_rf.fit(X_train, y_train)

model_lr = LogisticRegression(penalty='l2', solver='liblinear')
model_lr.fit(X_train, y_train)

model_svm = SVC(kernel='rbf', C=0.25)
model_svm.fit(X_train, y_train)

# Hyperparameter tuning for Gradient Boosting
param_grid = {
    'n_estimators': [50, 100, 150],
    'learning_rate': [0.01, 0.05, 0.1],
    'max_depth': [3, 5, 7]
}
grid_search = GridSearchCV(GradientBoostingClassifier(random_state=42), param_grid, cv=5)
grid_search.fit(X_train, y_train)

best_params = grid_search.best_params_
print(f"🔍 Best GB Parameters: {best_params}")

# Train the optimized Gradient Boosting model
model_gb = GradientBoostingClassifier(**best_params, random_state=42)
model_gb.fit(X_train, y_train)

# Evaluate Model Performance
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores_rf = cross_val_score(model_rf, X_resampled, y_resampled, cv=cv)
cv_scores_lr = cross_val_score(model_lr, X_resampled, y_resampled, cv=cv)
cv_scores_svm = cross_val_score(model_svm, X_resampled, y_resampled, cv=cv)
cv_scores_gb = cross_val_score(model_gb, X_resampled, y_resampled, cv=cv)

accuracy_rf = model_rf.score(X_test, y_test)
accuracy_lr = model_lr.score(X_test, y_test)
accuracy_svm = model_svm.score(X_test, y_test)
accuracy_gb = model_gb.score(X_test, y_test)

# Print Final Evaluation Results
print(f"✅ Random Forest Test Accuracy: {accuracy_rf:.2f}")
print(f"✅ Logistic Regression Test Accuracy: {accuracy_lr:.2f}")
print(f"✅ Support Vector Machine Test Accuracy: {accuracy_svm:.2f}")
print(f"✅ Optimized Gradient Boosting Test Accuracy: {accuracy_gb:.2f}")

print("\n📊 Feature Correlations:")
print(X.corr())
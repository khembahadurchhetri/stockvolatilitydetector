import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from imblearn.over_sampling import SMOTE

def run_pipeline(file_path):
    # Step 1: Load Data
    df = pd.read_csv(file_path)

    # Step 2: Feature Engineering
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    
    df["MACD"] = df["Close"].ewm(span=12).mean() - df["Close"].ewm(span=26).mean()
    df["ATR"] = (df["High"] - df["Low"]).rolling(window=14).mean()

    # Step 3: Rolling Standard Deviation
    window_size = 14
    rolling_std = np.std(np.lib.stride_tricks.sliding_window_view(df["Close"], window_size), axis=1)

    df = df.iloc[window_size - 1:].copy()
    df["Rolling_Std_NumPy"] = rolling_std

    # Step 4: Refine Features & Target
    X = df[["Close", "Volume", "RSI", "MACD", "ATR"]]
    y = (df["Rolling_Std_NumPy"] > df["Rolling_Std_NumPy"].quantile(0.75)).astype(int)

    X = X.dropna().copy()
    y = y.loc[X.index]

    # Step 5: SMOTE Balancing
    smote = SMOTE(sampling_strategy=0.75, random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)

    # Step 6: Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.3, random_state=42)

    # Step 7: Train Classifiers
    model_rf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    model_rf.fit(X_train, y_train)

    model_lr = LogisticRegression(l1_ratio=0, solver='liblinear')
    model_lr.fit(X_train, y_train)

    model_svm = SVC(kernel='rbf', C=0.25, probability=True)
    model_svm.fit(X_train, y_train)

    model_gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
    model_gb.fit(X_train, y_train)

    results = {
        "Random Forest": model_rf.score(X_test, y_test),
        "Logistic Regression": model_lr.score(X_test, y_test),
        "SVM": model_svm.score(X_test, y_test),
        "Gradient Boosting": model_gb.score(X_test, y_test)
    }
    
    return results, X.corr(), df
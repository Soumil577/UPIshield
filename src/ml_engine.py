"""
Optional Machine Learning Anomaly Detection Layer for UPIShield.
Utilizes scikit-learn's Isolation Forest to provide an auxiliary unsupervised
anomaly score alongside the deterministic rule and behavioral engines.
"""

from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd

from src.behavior import extract_hour_from_time_or_ts

try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class MLAnomalyEngine:
    """
    Lightweight Isolation Forest anomaly detector.
    Provides graceful fallback if scikit-learn is unavailable.
    """

    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.is_available = SKLEARN_AVAILABLE
        self.is_trained = False
        self.model = None
        self.contamination = contamination
        self.random_state = random_state

        if self.is_available:
            self.model = IsolationForest(
                n_estimators=50,
                contamination=contamination,
                random_state=random_state
            )

    def _extract_features(self, df_or_tx: Any) -> np.ndarray:
        """Extracts numerical features [amount, hour, frequency, device_new, beneficiary_new]."""
        if isinstance(df_or_tx, dict):
            amt = float(df_or_tx.get("amount", 0.0))
            hr = extract_hour_from_time_or_ts(df_or_tx)
            freq = float(df_or_tx.get("transaction_frequency", 1.0))
            dev_new = 1.0 if (df_or_tx.get("device_new") or df_or_tx.get("device_new") == 1) else 0.0
            ben_new = 1.0 if (df_or_tx.get("beneficiary_new") or df_or_tx.get("beneficiary_new") == 1) else 0.0
            return np.array([[amt, hr, freq, dev_new, ben_new]], dtype=float)

        elif isinstance(df_or_tx, pd.DataFrame):
            df = df_or_tx.copy()
            amts = df["amount"].astype(float).values
            
            hours = []
            for _, row in df.iterrows():
                hours.append(extract_hour_from_time_or_ts(row.to_dict()))
            hours = np.array(hours, dtype=float)

            freqs = df["transaction_frequency"].astype(float).values if "transaction_frequency" in df.columns else np.ones(len(df))
            devs = df["device_new"].astype(float).values if "device_new" in df.columns else np.zeros(len(df))
            bens = df["beneficiary_new"].astype(float).values if "beneficiary_new" in df.columns else np.zeros(len(df))

            return np.column_stack([amts, hours, freqs, devs, bens])
        
        return np.zeros((1, 5))

    def train_on_history(self, history_df: pd.DataFrame) -> bool:
        """Trains the Isolation Forest model on historical transactions."""
        if not self.is_available or history_df is None or len(history_df) < 10:
            self.is_trained = False
            return False

        try:
            # Train only on normal baseline transactions
            train_df = history_df[history_df["fraud_label"] == 0] if "fraud_label" in history_df.columns else history_df
            if len(train_df) < 5:
                train_df = history_df

            X = self._extract_features(train_df)
            self.model.fit(X)
            self.is_trained = True
            return True
        except Exception:
            self.is_trained = False
            return False

    def predict_anomaly_score(self, tx: Dict[str, Any]) -> Optional[float]:
        """
        Computes an anomaly score scaled 0 - 100 where higher = more anomalous.
        Returns None if model is untrained or unavailable.
        """
        if not self.is_available or not self.is_trained or self.model is None:
            return None

        try:
            X = self._extract_features(tx)
            # IsolationForest score_samples: lower score means more abnormal (negative values)
            raw_score = self.model.score_samples(X)[0]
            # Map raw score (typically -0.8 to -0.2) into 0-100 anomaly scale
            # -0.8 -> ~95, -0.4 -> ~40, -0.3 -> ~15
            mapped_score = (0.5 - raw_score) * 100.0
            anomaly_score = min(100.0, max(0.0, round(mapped_score, 1)))
            return anomaly_score
        except Exception:
            return None


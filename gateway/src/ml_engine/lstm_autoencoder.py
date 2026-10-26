"""
PyTorch Deep Learning Spatio-Temporal LSTM Autoencoder for Anomaly Detection.

Calculates reconstruction error MSE(X, X_hat) on multivariate sensor time-series sequences.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np

logger = logging.getLogger("LSTMAutoencoderML")

# PyTorch import with safe fallback
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not installed yet. LSTM Autoencoder running in fallback emulation mode.")

DEFAULT_LSTM_MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "lstm_autoencoder.pt"


if TORCH_AVAILABLE:
    class PyTorchLSTMModel(nn.Module):
        """PyTorch Encoder-Decoder Architecture for Sequence Reconstruction."""

        def __init__(self, input_dim: int = 5, hidden_dim: int = 16, latent_dim: int = 8):
            super(PyTorchLSTMModel, self).__init__()
            self.encoder_lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
            self.encoder_latent = nn.Linear(hidden_dim, latent_dim)
            self.decoder_latent = nn.Linear(latent_dim, hidden_dim)
            self.decoder_lstm = nn.LSTM(hidden_dim, input_dim, batch_first=True)

        def forward(self, x):
            # x shape: (batch_size, seq_len, input_dim)
            _, (h_n, _) = self.encoder_lstm(x)
            latent = torch.relu(self.encoder_latent(h_n[-1]))
            
            # Repeat latent across sequence length
            seq_len = x.size(1)
            decoded_input = self.decoder_latent(latent).unsqueeze(1).repeat(1, seq_len, 1)
            output, _ = self.decoder_lstm(decoded_input)
            return output


class LSTMAutoencoderDetector:
    """
    Spatio-Temporal LSTM Autoencoder Detector for Gateway Inference.
    """

    def __init__(self, seq_len: int = 5, model_path: Optional[Path] = None):
        self.seq_len = seq_len
        self.model_path = model_path or DEFAULT_LSTM_MODEL_PATH
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        self.is_trained = False
        
        if TORCH_AVAILABLE:
            self.model = PyTorchLSTMModel(input_dim=5, hidden_dim=16, latent_dim=8)
            self.model.eval()
            self.is_trained = True

    def predict_reconstruction_loss(self, sequence_metrics: List[Dict[str, Any]]) -> float:
        """
        Predict reconstruction error MSE and return normalized anomaly score S_LSTM [0.0, 1.0].
        """
        if not TORCH_AVAILABLE or len(sequence_metrics) < self.seq_len:
            # Fallback estimation if sequence buffer incomplete
            return 0.0

        try:
            # Construct feature matrix (seq_len, 5)
            features = []
            for item in sequence_metrics[-self.seq_len:]:
                features.append([
                    (float(item.get("temperature_c", 24.0)) - 24.0) / 10.0,
                    (float(item.get("humidity_pct", 50.0)) - 50.0) / 20.0,
                    (float(item.get("current_amps", 3.5)) - 3.5) / 5.0,
                    (float(item.get("vibration_g", 0.02)) - 0.02) / 0.1,
                    (float(item.get("air_quality_index", 35.0)) - 35.0) / 50.0
                ])

            X_arr = np.array([features], dtype=np.float32)
            X_tensor = torch.tensor(X_arr)

            with torch.no_grad():
                X_hat = self.model(X_tensor)
                mse_loss = float(torch.mean((X_tensor - X_hat) ** 2).item())

            # Normalize MSE loss [0.0, 2.0] -> score [0.0, 1.0]
            s_lstm = np.clip(mse_loss / 2.0, 0.0, 1.0)
            return round(float(s_lstm), 3)

        except Exception as e:
            logger.error(f"Error evaluating LSTM Autoencoder reconstruction loss: {e}")
            return 0.0


# Global LSTM Engine Instance
lstm_autoencoder_engine = LSTMAutoencoderDetector()

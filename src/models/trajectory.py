"""
src/models/trajectory.py
LSTM-based trajectory model for placement probability prediction.

Architecture
------------
  Input  : (batch, N_SEMESTERS=8, input_size=6)
  LSTM   : 2 layers, hidden=64, dropout=0.2
  Output : scalar sigmoid → P(placement)
"""
from __future__ import annotations

import os
from typing import List, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader


DEVICE = torch.device("cpu")
MODEL_PATH = os.path.join("models", "trajectory_model.pt")


# ── Dataset ───────────────────────────────────────────────────────────────────

class TrajectoryDataset(Dataset):
    def __init__(self, X: np.ndarray, y: np.ndarray) -> None:
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: int):
        return self.X[idx], self.y[idx]


# ── Model ─────────────────────────────────────────────────────────────────────

class TrajectoryLSTM(nn.Module):
    """
    2-layer LSTM → dropout → FC → sigmoid.
    Input shape: (batch, seq_len, input_size)
    Output shape: (batch,) probabilities
    """

    def __init__(self, input_size: int = 6, hidden_size: int = 64,
                 num_layers: int = 2, dropout: float = 0.2) -> None:
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, input_size)
        out, _ = self.lstm(x)          # (batch, seq_len, hidden)
        last   = out[:, -1, :]        # take final timestep
        last   = self.dropout(last)
        logit  = self.fc(last).squeeze(-1)
        return torch.sigmoid(logit)


# ── Training ──────────────────────────────────────────────────────────────────

def train_trajectory_model(
    X: np.ndarray,
    y: np.ndarray,
    epochs: int = 30,
    batch_size: int = 128,
    lr: float = 1e-3,
) -> TrajectoryLSTM:
    """
    Train the LSTM trajectory model and return it.

    Parameters
    ----------
    X : (N, 8, 6)  float32
    y : (N,)       float32  placement labels
    """
    dataset = TrajectoryDataset(X, y)
    split   = int(0.85 * len(dataset))
    train_ds, val_ds = torch.utils.data.random_split(
        dataset, [split, len(dataset) - split],
        generator=torch.Generator().manual_seed(42),
    )
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size)

    model     = TrajectoryLSTM(input_size=X.shape[2]).to(DEVICE)
    criterion = nn.BCELoss()
    optimiser = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.StepLR(optimiser, step_size=10, gamma=0.5)

    best_val_loss = float("inf")
    best_state    = None

    for epoch in range(1, epochs + 1):
        # ── Train ──
        model.train()
        train_loss = 0.0
        for xb, yb in train_loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            optimiser.zero_grad()
            pred = model(xb)
            loss = criterion(pred, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimiser.step()
            train_loss += loss.item() * len(yb)
        train_loss /= len(train_ds)

        # ── Validate ──
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                val_loss += criterion(model(xb), yb).item() * len(yb)
        val_loss /= len(val_ds)
        scheduler.step()

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.clone() for k, v in model.state_dict().items()}

        if epoch % 5 == 0:
            print(f"  [LSTM] Epoch {epoch:3d}/{epochs}  train={train_loss:.4f}  val={val_loss:.4f}")

    if best_state is not None:
        model.load_state_dict(best_state)
    return model


# ── Inference helpers ─────────────────────────────────────────────────────────

def save_trajectory_model(model: TrajectoryLSTM, path: str = MODEL_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save(model.state_dict(), path)
    print(f"  [LSTM] Saved -> {path}")


def load_trajectory_model(path: str = MODEL_PATH, input_size: int = 6) -> TrajectoryLSTM:
    model = TrajectoryLSTM(input_size=input_size)
    model.load_state_dict(torch.load(path, map_location=DEVICE))
    model.eval()
    return model


def predict_trajectory(model: TrajectoryLSTM, sequence: np.ndarray) -> float:
    """
    Parameters
    ----------
    sequence : (N_SEMESTERS, input_size) float32 array

    Returns
    -------
    float : P(placement)
    """
    model.eval()
    with torch.no_grad():
        x = torch.tensor(sequence, dtype=torch.float32).unsqueeze(0).to(DEVICE)
        return float(model(x).item())


def synthesize_sequence_from_flat(sample: dict) -> np.ndarray:
    """
    Build a (8, 6) trajectory sequence from a flat feature dict.
    Used at inference when no explicit trajectory is available.
    """
    cgpa          = float(sample.get("cgpa", 7.0))
    skills        = float(sample.get("skills", 0.3))
    internship    = float(sample.get("internship", 0))
    market_demand = float(sample.get("market_demand", 0.7))
    portal        = float(sample.get("portal_activity", 0.5))

    seq = []
    for sem in range(8):
        t = sem / 7.0
        seq.append([
            (cgpa / 10.0) * (0.8 + 0.2 * t),         # cgpa ramp
            skills * t,                                 # cumulative skills
            internship * float(sem >= 4),               # internship after sem4
            market_demand,
            portal * (0.8 + 0.2 * t),                  # engagement grows
            portal,
        ])
    return np.array(seq, dtype=np.float32)

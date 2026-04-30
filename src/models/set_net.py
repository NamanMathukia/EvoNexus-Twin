"""
src/models/set_net.py
LGDESetNet approximation — learns skill set interaction effects.

Architecture
------------
  Embedding(vocab_size, embed_dim)
  Mean Pool over set
  FC(embed_dim → 64 → 32 → 1) → sigmoid
"""
from __future__ import annotations

import os
from typing import List, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

DEVICE     = torch.device("cpu")
MODEL_PATH = os.path.join("models", "set_net_model.pt")

from src.data.generator import SKILL_VOCAB_SIZE


# ── Dataset ───────────────────────────────────────────────────────────────────

class SkillSetDataset(Dataset):
    """
    Variable-length skill index lists padded to a fixed max size.
    Padding index = SKILL_VOCAB_SIZE (out-of-vocab).
    """

    def __init__(self, skill_sets: List[List[int]], labels: np.ndarray,
                 max_len: int = 30) -> None:
        self.max_len = max_len
        self.labels  = torch.tensor(labels, dtype=torch.float32)
        padded = []
        masks  = []
        for skill_list in skill_sets:
            trunc = skill_list[:max_len]
            pad_len = max_len - len(trunc)
            padded.append(trunc + [SKILL_VOCAB_SIZE] * pad_len)
            masks.append([1] * len(trunc) + [0] * pad_len)
        self.X    = torch.tensor(padded, dtype=torch.long)
        self.mask = torch.tensor(masks,  dtype=torch.float32)

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int):
        return self.X[idx], self.mask[idx], self.labels[idx]


# ── Model ─────────────────────────────────────────────────────────────────────

class LGDESetNet(nn.Module):
    """
    Embedding → Masked Mean Pool → FC stack → sigmoid.
    Uses a padding embedding (vocab_size+1 rows) so padded tokens are zeroed.
    """

    def __init__(self, vocab_size: int = SKILL_VOCAB_SIZE,
                 embed_dim: int = 32, dropout: float = 0.2) -> None:
        super().__init__()
        # +1 row for the padding index
        self.embed = nn.Embedding(vocab_size + 1, embed_dim,
                                  padding_idx=vocab_size)
        self.fc = nn.Sequential(
            nn.Linear(embed_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        # x: (batch, max_len)   mask: (batch, max_len)
        emb    = self.embed(x)                   # (batch, max_len, embed_dim)
        mask_e = mask.unsqueeze(-1)              # (batch, max_len, 1)
        pooled = (emb * mask_e).sum(1) / (mask_e.sum(1).clamp(min=1e-8))
        logit  = self.fc(pooled).squeeze(-1)
        return torch.sigmoid(logit)


# ── Training ──────────────────────────────────────────────────────────────────

def train_set_net(
    skill_sets: List[List[int]],
    y: np.ndarray,
    epochs: int = 30,
    batch_size: int = 128,
    lr: float = 1e-3,
) -> LGDESetNet:
    dataset = SkillSetDataset(skill_sets, y)
    split   = int(0.85 * len(dataset))
    train_ds, val_ds = torch.utils.data.random_split(
        dataset, [split, len(dataset) - split],
        generator=torch.Generator().manual_seed(42),
    )
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size)

    model     = LGDESetNet().to(DEVICE)
    criterion = nn.BCELoss()
    optimiser = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.StepLR(optimiser, step_size=10, gamma=0.5)

    best_val  = float("inf")
    best_state = None

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for xb, mb, yb in train_loader:
            xb, mb, yb = xb.to(DEVICE), mb.to(DEVICE), yb.to(DEVICE)
            optimiser.zero_grad()
            pred = model(xb, mb)
            loss = criterion(pred, yb)
            loss.backward()
            optimiser.step()
            train_loss += loss.item() * len(yb)
        train_loss /= len(train_ds)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for xb, mb, yb in val_loader:
                xb, mb, yb = xb.to(DEVICE), mb.to(DEVICE), yb.to(DEVICE)
                val_loss += criterion(model(xb, mb), yb).item() * len(yb)
        val_loss /= len(val_ds)
        scheduler.step()

        if val_loss < best_val:
            best_val   = val_loss
            best_state = {k: v.clone() for k, v in model.state_dict().items()}

        if epoch % 5 == 0:
            print(f"  [SetNet] Epoch {epoch:3d}/{epochs}  train={train_loss:.4f}  val={val_loss:.4f}")

    if best_state is not None:
        model.load_state_dict(best_state)
    return model


# ── Inference helpers ─────────────────────────────────────────────────────────

def save_set_net(model: LGDESetNet, path: str = MODEL_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save(model.state_dict(), path)
    print(f"  [SetNet] Saved -> {path}")


def load_set_net(path: str = MODEL_PATH) -> LGDESetNet:
    model = LGDESetNet()
    model.load_state_dict(torch.load(path, map_location=DEVICE))
    model.eval()
    return model


def predict_set_placement(model: LGDESetNet, skill_indices: List[int]) -> float:
    """
    Parameters
    ----------
    skill_indices : list of int  (skill IDs from SKILL_TO_IDX)

    Returns
    -------
    float : P(placement)
    """
    if not skill_indices:
        skill_indices = [0]
    dataset = SkillSetDataset([skill_indices], np.array([0.0]))
    x, m, _ = dataset[0]
    model.eval()
    with torch.no_grad():
        return float(model(x.unsqueeze(0), m.unsqueeze(0)).item())

"""Convolutional baseline of stage 25 (docs/PREDICTIONS.md): a small dilated fully convolutional network that maps a
coarse elevation model to a per cell face probability, trained leave one site out on lidar labels.

Registered design, not tuned: two input channels (elevation minus its 7 x 7 mean, divided by the posting, and the slope),
four 3 x 3 convolutions of 32 channels with dilations 1, 2, 4 and 8 and ReLU, a 1 x 1 convolution to one logit; binary
cross entropy; Adam, learning rate 0.001; 1500 steps of 16 random crops (64 x 64 cells at 10 m, 32 x 32 at 30 m) with
flips and quarter turns; seed 0. Needs torch (CPU is enough); SIMULATED BY ME.
"""
from __future__ import annotations
import numpy as np
from scipy.ndimage import uniform_filter

from .benchmark import slope_tan

STEPS, BATCH, LR, SEED = 1500, 16, 1e-3, 0


def channels(z: np.ndarray, d: float) -> np.ndarray:
    return np.stack([(z - uniform_filter(z, 7, mode="nearest")) / d, slope_tan(z, d)]).astype(np.float32)


def _net():
    import torch.nn as nn
    layers, cin = [], 2
    for dil in (1, 2, 4, 8):
        layers += [nn.Conv2d(cin, 32, 3, padding=dil, dilation=dil, padding_mode="reflect"), nn.ReLU()]
        cin = 32
    layers.append(nn.Conv2d(32, 1, 1))
    return nn.Sequential(*layers)


def fit(train: list, crop: int, steps: int = STEPS, seed: int = SEED):
    """train: list of (channels (2, H, W), labels (H, W) bool). Returns the trained network."""
    import torch
    torch.manual_seed(seed)
    torch.set_num_threads(max(1, torch.get_num_threads()))
    rng = np.random.default_rng(seed)
    net = _net()
    opt = torch.optim.Adam(net.parameters(), lr=LR)
    lossf = torch.nn.BCEWithLogitsLoss()
    usable = [(x, y) for x, y in train if min(y.shape) >= crop]
    if not usable:
        raise ValueError("no training grid is as large as the crop")
    sizes = np.array([y.size for _, y in usable], float)
    pick_p = sizes / sizes.sum()
    for _ in range(steps):
        xs, ys = [], []
        for _ in range(BATCH):
            x, y = usable[rng.choice(len(usable), p=pick_p)]
            r = rng.integers(0, y.shape[0] - crop + 1); c = rng.integers(0, y.shape[1] - crop + 1)
            xb, yb = x[:, r:r + crop, c:c + crop], y[r:r + crop, c:c + crop]
            q = rng.integers(0, 4)
            xb, yb = np.rot90(xb, q, axes=(1, 2)), np.rot90(yb, q)
            if rng.random() < 0.5:
                xb, yb = xb[:, :, ::-1], yb[:, ::-1]
            xs.append(np.ascontiguousarray(xb)); ys.append(np.ascontiguousarray(yb))
        xt = torch.from_numpy(np.stack(xs)); yt = torch.from_numpy(np.stack(ys).astype(np.float32))[:, None]
        opt.zero_grad()
        loss = lossf(net(xt), yt)
        loss.backward()
        opt.step()
    return net


def predict(net, x: np.ndarray) -> np.ndarray:
    import torch
    with torch.no_grad():
        return torch.sigmoid(net(torch.from_numpy(x[None]))).numpy()[0, 0]

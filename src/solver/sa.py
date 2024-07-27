import math
import random


class SimulatedAnnealing:
    def __init__(self, T0, T1, n_iter):
        self.T0 = T0
        self.T1 = T1
        self.n_iter = n_iter
        self.iter = 0

    def temperature(self) -> float:
        progress = self.iter / self.n_iter
        remain = 1 - progress
        eps = 1e-10
        t = math.pow(self.T0, remain) * math.pow(self.T1, progress) + eps
        return t

    def accept(self, d_worsen) -> bool:
        lower = -10.0
        upper = 1.0
        index = max(-d_worsen / self.temperature(), lower)
        index = min(index, upper)
        p_accept = math.exp(index)
        self.iter += 1
        return d_worsen <= 0 or random.random() < p_accept

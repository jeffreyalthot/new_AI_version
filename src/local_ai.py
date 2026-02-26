"""Prototype d'IA locale auto-organisée.

Ce module implémente 5 principes:
- Système auto-organisé
- Continuité temporelle
- Régulation corporelle
- Intégration hormonale
- Auto-modélisation constante
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
import json
import math
import random
import time


@dataclass
class HormonalState:
    cortisol: float = 0.3   # stress
    dopamine: float = 0.5   # motivation/récompense
    serotonin: float = 0.5  # stabilité de l'humeur
    melatonin: float = 0.2  # repos/fatigue

    def integrate(self, body: "BodyState", external_stress: float, novelty: float) -> None:
        """Met à jour les hormones selon le corps et l'environnement."""
        self.cortisol = clamp(self.cortisol * 0.85 + external_stress * 0.15 + (1 - body.energy) * 0.08)
        self.dopamine = clamp(self.dopamine * 0.80 + novelty * 0.20 - self.cortisol * 0.05)
        self.serotonin = clamp(self.serotonin * 0.90 + body.balance * 0.10 - self.cortisol * 0.04)
        self.melatonin = clamp(self.melatonin * 0.92 + (1 - body.energy) * 0.08)


@dataclass
class BodyState:
    energy: float = 0.8
    temperature: float = 0.5
    hydration: float = 0.7

    @property
    def balance(self) -> float:
        # Mesure globale d'équilibre corporel.
        return clamp((self.energy + self.hydration + (1 - abs(self.temperature - 0.5) * 2)) / 3)

    def regulate(self, actions: Dict[str, float]) -> None:
        """Boucle de régulation corporelle (homéostasie)."""
        self.energy = clamp(self.energy + actions.get("rest", 0) * 0.09 - 0.03)
        self.hydration = clamp(self.hydration + actions.get("drink", 0) * 0.12 - 0.015)
        thermal_push = actions.get("cool", 0) * -0.07 + actions.get("warm", 0) * 0.07
        self.temperature = clamp(self.temperature + thermal_push + random.uniform(-0.015, 0.015))


@dataclass
class SelfModel:
    confidence: float = 0.5
    coherence: float = 0.5
    priorities: Dict[str, float] = field(default_factory=lambda: {
        "survival": 0.7,
        "exploration": 0.5,
        "social": 0.4,
    })

    def update(self, body: BodyState, hormones: HormonalState, memory: List[Dict]) -> None:
        """Auto-modélisation constante fondée sur l'historique."""
        recent = memory[-15:] if memory else []
        avg_balance = sum(item["body_balance"] for item in recent) / len(recent) if recent else body.balance
        reward_trend = sum(item["reward"] for item in recent) / len(recent) if recent else 0.0

        self.coherence = clamp(self.coherence * 0.85 + avg_balance * 0.10 + (1 - hormones.cortisol) * 0.05)
        self.confidence = clamp(self.confidence * 0.85 + reward_trend * 0.10 + self.coherence * 0.05)

        # Auto-organisation des priorités
        self.priorities["survival"] = clamp(0.9 - body.energy * 0.4 + hormones.cortisol * 0.5)
        self.priorities["exploration"] = clamp(0.2 + hormones.dopamine * 0.7 - hormones.melatonin * 0.3)
        self.priorities["social"] = clamp(0.3 + hormones.serotonin * 0.6)


@dataclass
class LocalOrganizingAI:
    body: BodyState = field(default_factory=BodyState)
    hormones: HormonalState = field(default_factory=HormonalState)
    self_model: SelfModel = field(default_factory=SelfModel)
    memory: List[Dict] = field(default_factory=list)
    t: int = 0

    def step(self, sensory_input: Dict[str, float]) -> Dict:
        """Un pas cognitif avec continuité temporelle."""
        self.t += 1

        novelty = sensory_input.get("novelty", 0.0)
        external_stress = sensory_input.get("stress", 0.0)

        # 1) Intégration hormonale
        self.hormones.integrate(self.body, external_stress=external_stress, novelty=novelty)

        # 2) Choix auto-organisé d'actions
        actions = self.decide_actions(novelty)

        # 3) Régulation corporelle
        self.body.regulate(actions)

        # 4) Récompense interne
        reward = self.compute_internal_reward()

        # 5) Continuité temporelle + mémoire
        snapshot = {
            "t": self.t,
            "input": sensory_input,
            "actions": actions,
            "reward": reward,
            "body_balance": self.body.balance,
            "hormones": self.hormones.__dict__.copy(),
        }
        self.memory.append(snapshot)

        # 6) Auto-modélisation constante
        self.self_model.update(self.body, self.hormones, self.memory)

        return {
            "time": self.t,
            "actions": actions,
            "reward": round(reward, 3),
            "body": {
                "energy": round(self.body.energy, 3),
                "temperature": round(self.body.temperature, 3),
                "hydration": round(self.body.hydration, 3),
                "balance": round(self.body.balance, 3),
            },
            "hormones": {k: round(v, 3) for k, v in self.hormones.__dict__.items()},
            "self_model": {
                "confidence": round(self.self_model.confidence, 3),
                "coherence": round(self.self_model.coherence, 3),
                "priorities": {k: round(v, 3) for k, v in self.self_model.priorities.items()},
            },
        }

    def decide_actions(self, novelty: float) -> Dict[str, float]:
        """Politique émergente basée sur les besoins internes."""
        p = self.self_model.priorities
        rest = sigmoid((0.55 - self.body.energy) * 4 + self.hormones.melatonin * 2)
        drink = sigmoid((0.65 - self.body.hydration) * 4)
        cool = sigmoid((self.body.temperature - 0.55) * 10)
        warm = sigmoid((0.45 - self.body.temperature) * 10)

        explore = clamp(p["exploration"] * (0.5 + novelty))
        social_ping = clamp(p["social"] * self.self_model.confidence)

        return {
            "rest": rest,
            "drink": drink,
            "cool": cool,
            "warm": warm,
            "explore": explore,
            "social_ping": social_ping,
        }

    def compute_internal_reward(self) -> float:
        b = self.body.balance
        h = (self.hormones.dopamine + self.hormones.serotonin - self.hormones.cortisol) / 2
        c = self.self_model.coherence
        return clamp(0.5 * b + 0.2 * h + 0.3 * c)


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def run_demo(steps: int = 20, seed: int = 42) -> None:
    random.seed(seed)
    ai = LocalOrganizingAI()

    print("=== Démo IA locale auto-organisée ===")
    for _ in range(steps):
        sensory = {
            "novelty": random.random(),
            "stress": random.random() * 0.6,
        }
        state = ai.step(sensory)
        print(json.dumps(state, ensure_ascii=False))
        time.sleep(0.05)


if __name__ == "__main__":
    run_demo()

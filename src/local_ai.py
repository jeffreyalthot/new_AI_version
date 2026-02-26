"""Prototype d'IA locale auto-organisée avec monde 3D et lignée d'agents.

Ce module implémente 5 principes:
- Système auto-organisé
- Continuité temporelle
- Régulation corporelle
- Intégration hormonale
- Auto-modélisation constante

Extensions:
- Monde 3D explorable en continu (temps réel)
- Cube de lumière qui sauvegarde l'"âme" d'un agent décédé
- Sexe biologique (male/feminin) et reproduction male/feminin
- Démarrage avec 2 IA dans des conditions optimales de bien-être
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import json
import math
import random
import time


SEXES = ("male", "feminin")


@dataclass
class HormonalState:
    cortisol: float = 0.2   # stress
    dopamine: float = 0.7   # motivation/récompense
    serotonin: float = 0.75  # stabilité de l'humeur
    melatonin: float = 0.25  # repos/fatigue

    def integrate(self, body: "BodyState", external_stress: float, novelty: float) -> None:
        """Met à jour les hormones selon le corps et l'environnement."""
        self.cortisol = clamp(self.cortisol * 0.85 + external_stress * 0.15 + (1 - body.energy) * 0.08)
        self.dopamine = clamp(self.dopamine * 0.80 + novelty * 0.20 - self.cortisol * 0.05)
        self.serotonin = clamp(self.serotonin * 0.90 + body.balance * 0.10 - self.cortisol * 0.04)
        self.melatonin = clamp(self.melatonin * 0.92 + (1 - body.energy) * 0.08)


@dataclass
class BodyState:
    energy: float = 0.95
    temperature: float = 0.5
    hydration: float = 0.9

    @property
    def balance(self) -> float:
        # Mesure globale d'équilibre corporel.
        return clamp((self.energy + self.hydration + (1 - abs(self.temperature - 0.5) * 2)) / 3)

    def regulate(self, actions: Dict[str, float], terrain_factor: float = 1.0) -> None:
        """Boucle de régulation corporelle (homéostasie)."""
        move_cost = actions.get("move", 0) * 0.02 * terrain_factor
        self.energy = clamp(self.energy + actions.get("rest", 0) * 0.09 - 0.018 - move_cost)
        self.hydration = clamp(self.hydration + actions.get("drink", 0) * 0.12 - 0.012 - move_cost * 0.6)
        thermal_push = actions.get("cool", 0) * -0.07 + actions.get("warm", 0) * 0.07
        self.temperature = clamp(self.temperature + thermal_push + random.uniform(-0.01, 0.01))


@dataclass
class SelfModel:
    confidence: float = 0.8
    coherence: float = 0.8
    happiness: float = 0.85
    priorities: Dict[str, float] = field(default_factory=lambda: {
        "survival": 0.55,
        "exploration": 0.65,
        "social": 0.65,
        "legacy": 0.55,
    })

    def update(self, body: BodyState, hormones: HormonalState, memory: List[Dict], alive: bool) -> None:
        """Auto-modélisation constante fondée sur l'historique."""
        recent = memory[-20:] if memory else []
        avg_balance = sum(item["body_balance"] for item in recent) / len(recent) if recent else body.balance
        reward_trend = sum(item["reward"] for item in recent) / len(recent) if recent else 0.0

        self.coherence = clamp(self.coherence * 0.85 + avg_balance * 0.10 + (1 - hormones.cortisol) * 0.05)
        self.confidence = clamp(self.confidence * 0.82 + reward_trend * 0.12 + self.coherence * 0.06)
        self.happiness = clamp((body.balance * 0.42) + (hormones.serotonin * 0.35) + (self.coherence * 0.23))

        # Auto-organisation des priorités
        self.priorities["survival"] = clamp(0.85 - body.energy * 0.35 + hormones.cortisol * 0.45)
        self.priorities["exploration"] = clamp(0.25 + hormones.dopamine * 0.6 - hormones.melatonin * 0.2)
        self.priorities["social"] = clamp(0.3 + hormones.serotonin * 0.6)
        self.priorities["legacy"] = clamp(0.2 + self.happiness * 0.5 + (0.15 if alive else -0.1))


@dataclass
class SoulLightCube:
    """Cube lumineux mémorisant l'essence d'un agent après son décès."""

    soul_archive: Dict[str, Dict] = field(default_factory=dict)

    def store_soul(self, agent: "AgentAI") -> Dict:
        essence = {
            "name": agent.name,
            "sex": agent.sex,
            "age_seconds": round(agent.age_seconds, 3),
            "happiness": round(agent.self_model.happiness, 3),
            "confidence": round(agent.self_model.confidence, 3),
            "coherence": round(agent.self_model.coherence, 3),
            "last_position": tuple(round(v, 2) for v in agent.position),
            "memory_tail": agent.memory[-5:],
        }
        self.soul_archive[agent.name] = essence
        return essence


@dataclass
class AgentAI:
    name: str
    sex: str
    position: Tuple[float, float, float]
    body: BodyState = field(default_factory=BodyState)
    hormones: HormonalState = field(default_factory=HormonalState)
    self_model: SelfModel = field(default_factory=SelfModel)
    memory: List[Dict] = field(default_factory=list)
    alive: bool = True
    age_seconds: float = 0.0
    cooldown_reproduction: float = 0.0

    def step(
        self,
        sensory_input: Dict[str, float],
        terrain_factor: float = 1.0,
        elapsed_seconds: float = 1.0,
    ) -> Dict:
        """Un pas cognitif avec continuité temporelle."""
        if not self.alive:
            return {"name": self.name, "alive": False}

        self.age_seconds += elapsed_seconds
        novelty = sensory_input.get("novelty", 0.0)
        external_stress = sensory_input.get("stress", 0.0)

        self.hormones.integrate(self.body, external_stress=external_stress, novelty=novelty)
        actions = self.decide_actions(novelty)
        self.body.regulate(actions, terrain_factor=terrain_factor)
        reward = self.compute_internal_reward()

        snapshot = {
            "t_seconds": round(self.age_seconds, 3),
            "input": sensory_input,
            "actions": actions,
            "reward": reward,
            "body_balance": self.body.balance,
            "hormones": self.hormones.__dict__.copy(),
        }
        self.memory.append(snapshot)
        self.self_model.update(self.body, self.hormones, self.memory, self.alive)

        if self.cooldown_reproduction > 0:
            self.cooldown_reproduction = max(0.0, self.cooldown_reproduction - elapsed_seconds)

        if self.body.energy < 0.05 and self.body.hydration < 0.05:
            self.alive = False

        return {
            "name": self.name,
            "sex": self.sex,
            "alive": self.alive,
            "age_seconds": round(self.age_seconds, 3),
            "actions": actions,
            "reward": round(reward, 3),
            "body": {
                "energy": round(self.body.energy, 3),
                "temperature": round(self.body.temperature, 3),
                "hydration": round(self.body.hydration, 3),
                "balance": round(self.body.balance, 3),
            },
            "happiness": round(self.self_model.happiness, 3),
            "hormones": {k: round(v, 3) for k, v in self.hormones.__dict__.items()},
        }

    def decide_actions(self, novelty: float) -> Dict[str, float]:
        """Politique émergente basée sur les besoins internes."""
        p = self.self_model.priorities
        rest = sigmoid((0.55 - self.body.energy) * 4 + self.hormones.melatonin * 2)
        drink = sigmoid((0.70 - self.body.hydration) * 4)
        cool = sigmoid((self.body.temperature - 0.55) * 10)
        warm = sigmoid((0.45 - self.body.temperature) * 10)

        explore = clamp(p["exploration"] * (0.5 + novelty))
        social_ping = clamp(p["social"] * self.self_model.confidence)
        move = clamp(0.4 * explore + 0.2 * social_ping)

        return {
            "rest": rest,
            "drink": drink,
            "cool": cool,
            "warm": warm,
            "explore": explore,
            "social_ping": social_ping,
            "move": move,
        }

    def compute_internal_reward(self) -> float:
        b = self.body.balance
        h = (self.hormones.dopamine + self.hormones.serotonin - self.hormones.cortisol) / 2
        c = self.self_model.coherence
        joy = self.self_model.happiness
        return clamp(0.36 * b + 0.2 * h + 0.24 * c + 0.2 * joy)


@dataclass
class World3D:
    """Monde 3D explorable avec boucle continue en temps réel."""

    size: Tuple[float, float, float] = (50.0, 50.0, 20.0)
    soul_cube: SoulLightCube = field(default_factory=SoulLightCube)
    agents: List[AgentAI] = field(default_factory=list)
    tick: int = 0

    def __post_init__(self) -> None:
        if not self.agents:
            # Conditions initiales optimales: 2 IA, complémentaires, bien hydratées/énergisées.
            self.agents = [
                AgentAI(name="AI_Origin_M", sex="male", position=(10.0, 10.0, 2.0)),
                AgentAI(name="AI_Origin_F", sex="feminin", position=(12.0, 10.0, 2.0)),
            ]

    def step(self, elapsed_seconds: float = 1.0) -> Dict:
        self.tick += 1
        updates = []
        births = []

        for agent in self.agents:
            if not agent.alive:
                continue

            sensory = {
                "novelty": random.random(),
                "stress": random.random() * 0.35,
            }
            terrain_factor = self.sample_terrain_effort(agent.position)
            state = agent.step(sensory, terrain_factor=terrain_factor, elapsed_seconds=elapsed_seconds)
            if state["alive"]:
                self.move_agent(agent, state["actions"]["move"])
            else:
                essence = self.soul_cube.store_soul(agent)
                state["soul_stored"] = essence
            updates.append(state)

        baby = self.try_reproduction()
        if baby:
            births.append(baby)

        return {
            "tick": self.tick,
            "population": sum(1 for a in self.agents if a.alive),
            "updates": updates,
            "births": births,
            "soul_cube": {"stored_souls": list(self.soul_cube.soul_archive.keys())},
        }

    def sample_terrain_effort(self, position: Tuple[float, float, float]) -> float:
        x, y, z = position
        roughness = (math.sin(x / 4) + math.cos(y / 5) + (z / self.size[2])) / 3
        return clamp(1.0 + roughness * 0.25, 0.8, 1.25)

    def move_agent(self, agent: AgentAI, intensity: float) -> None:
        dx = random.uniform(-1, 1) * intensity * 1.8
        dy = random.uniform(-1, 1) * intensity * 1.8
        dz = random.uniform(-0.4, 0.4) * intensity
        x = clamp(agent.position[0] + dx, 0.0, self.size[0])
        y = clamp(agent.position[1] + dy, 0.0, self.size[1])
        z = clamp(agent.position[2] + dz, 0.0, self.size[2])
        agent.position = (x, y, z)

    def try_reproduction(self) -> Optional[Dict]:
        viable = [a for a in self.agents if a.alive and a.age_seconds >= 12 and a.cooldown_reproduction == 0]
        males = [a for a in viable if a.sex == "male"]
        females = [a for a in viable if a.sex == "feminin"]
        if not males or not females:
            return None

        father = random.choice(males)
        mother = random.choice(females)
        distance = euclidean_distance(father.position, mother.position)
        pair_happiness = (father.self_model.happiness + mother.self_model.happiness) / 2

        if distance > 4.0 or pair_happiness < 0.55 or random.random() > 0.15:
            return None

        child_sex = random.choice(SEXES)
        child_name = f"AI_Child_{len(self.agents)+1}_{child_sex[0].upper()}"
        spawn = (
            (father.position[0] + mother.position[0]) / 2,
            (father.position[1] + mother.position[1]) / 2,
            clamp((father.position[2] + mother.position[2]) / 2 + 0.2, 0.0, self.size[2]),
        )
        child = AgentAI(name=child_name, sex=child_sex, position=spawn)
        child.body.energy = clamp((father.body.energy + mother.body.energy) / 2 + 0.05)
        child.body.hydration = clamp((father.body.hydration + mother.body.hydration) / 2 + 0.05)
        child.self_model.confidence = clamp((father.self_model.confidence + mother.self_model.confidence) / 2)
        child.self_model.coherence = clamp((father.self_model.coherence + mother.self_model.coherence) / 2)
        child.self_model.happiness = clamp((father.self_model.happiness + mother.self_model.happiness) / 2)

        father.cooldown_reproduction = 20.0
        mother.cooldown_reproduction = 25.0
        self.agents.append(child)

        return {
            "child": child.name,
            "sex": child.sex,
            "parents": [father.name, mother.name],
            "spawn": tuple(round(v, 2) for v in spawn),
        }


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def euclidean_distance(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def run_demo(realtime_seconds: Optional[float] = None, tick_interval: float = 0.1, seed: int = 42) -> None:
    """Exécute la simulation en continu temps réel, sans limite par défaut."""
    random.seed(seed)
    world = World3D()
    print("=== Monde 3D IA (temps réel) ===")

    start = time.time()
    last_tick = start
    while realtime_seconds is None or time.time() - start < realtime_seconds:
        now = time.time()
        elapsed = now - last_tick
        last_tick = now
        state = world.step(elapsed_seconds=elapsed)
        print(json.dumps(state, ensure_ascii=False))
        time.sleep(tick_interval)


if __name__ == "__main__":
    run_demo()

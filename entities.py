from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, List
from constants import EntityType, WHITE

@dataclass
class Stats:
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 5
    speed: int = 10
    vision_range: int = 8

@dataclass
class Resources:
    atp: int = 100
    protein: int = 50
    rna: int = 0
    max_atp: int = 100
    max_protein: int = 100
    max_rna: int = 50

@dataclass
class Entity:
    x: int
    y: int
    entity_type: EntityType
    stats: Stats = field(default_factory=Stats)
    is_alive: bool = True
    name: str = ""
    color: Tuple[int, int, int] = WHITE
    char: str = "?"
    ai_state: str = "idle"
    target: Optional['Entity'] = None

    def take_damage(self, damage: int) -> int:
        actual_damage = max(1, damage - self.stats.defense // 2)
        self.stats.hp -= actual_damage
        if self.stats.hp <= 0:
            self.stats.hp = 0
            self.is_alive = False
        return actual_damage

    def heal(self, amount: int):
        self.stats.hp = min(self.stats.max_hp, self.stats.hp + amount)

    def distance_to(self, other: 'Entity') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def distance_to_pos(self, x: int, y: int) -> float:
        return ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5

class Mutation:
    def __init__(self, name: str, description: str, stat_changes: Dict[str, int]):
        self.name = name
        self.description = description
        self.stat_changes = stat_changes

    def apply(self, entity: Entity, resources: Resources):
        for stat, value in self.stat_changes.items():
            if hasattr(entity.stats, stat):
                current = getattr(entity.stats, stat)
                setattr(entity.stats, stat, current + value)
            elif hasattr(resources, stat):
                current = getattr(resources, stat)
                setattr(resources, stat, current + value)

MUTATIONS = [
    Mutation("Усиленная оболочка", "+20 макс. HP", {"max_hp": 20, "hp": 20}),
    Mutation("Острые шипы", "+5 атака", {"attack": 5}),
    Mutation("Плотная мембрана", "+3 защита", {"defense": 3}),
    Mutation("Быстрая репликация", "+2 скорость", {"speed": 2}),
    Mutation("Улучшенные рецепторы", "+2 обзор", {"vision_range": 2}),
    Mutation("Энергетический резерв", "+30 макс. ATP", {"max_atp": 30}),
    Mutation("Протеиновый синтез", "+30 макс. белка", {"max_protein": 30}),
    Mutation("РНК оптимизация", "+20 макс. РНК", {"max_rna": 20}),
    Mutation("Агрессивный штамм", "+8 атака, -10 HP", {"attack": 8, "max_hp": -10}),
    Mutation("Защитная капсула", "+5 защита, -3 атака", {"defense": 5, "attack": -3}),
    Mutation("Метаболизм", "+2 ко всем ресурсам", {"max_atp": 20, "max_protein": 20, "max_rna": 10}),
]

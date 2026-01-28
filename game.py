import random
import math
import arcade
from typing import List, Optional
from constants import *
from entities import Entity, Stats, Resources, Mutation, MUTATIONS
from game_map import GameMap
from ui import UI, MessageLog

class Game:
    def __init__(self, screen: arcade.View):
        self.screen = screen
        self.ui = UI(screen)

        self.state = GameState.PLAYER_TURN
        self.current_level = 1
        self.turn_count = 0

        self.message_log = MessageLog()
        self.available_mutations: List[Mutation] = []
        self.camera_x = 0
        self.camera_y = 0

        self.player: Optional[Entity] = None
        self.resources: Optional[Resources] = None
        self.entities: List[Entity] = []
        self.virus_clones: List[Entity] = []
        self.game_map: Optional[GameMap] = None

    def init_new_game(self):
        self.current_level = 1
        self.turn_count = 0
        self.state = GameState.PLAYER_TURN

        # Создаем игрока
        self.player = Entity(
            x=0, y=0,
            entity_type=EntityType.PLAYER,
            stats=Stats(hp=100, max_hp=100, attack=12, defense=5, speed=10, vision_range=8),
            name="Вирус",
            color=GREEN,
            char="V"
        )

        self.resources = Resources()
        self.entities = [self.player]
        self.virus_clones = []

        self.message_log.clear()
        self.message_log.add("Вы проникли в организм. Захватите контроль!", CYAN)

        self.generate_level()

    def generate_level(self):
        self.game_map = GameMap(level=self.current_level)

        # Расположение игрока
        spawn_x, spawn_y = self.game_map.get_spawn_position()
        self.player.x = spawn_x
        self.player.y = spawn_y

        # Хранение живых клонов
        self.entities = [self.player]
        self.virus_clones = [c for c in self.virus_clones if c.is_alive]

        # Перемещаем клонов ближе к игроку
        for clone in self.virus_clones:
            placed = False
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)]:
                nx, ny = self.player.x + dx, self.player.y + dy
                if self.game_map.is_walkable(nx, ny) and not self.game_map.is_blocked(nx, ny, self.entities):
                    clone.x, clone.y = nx, ny
                    placed = True
                    break
            if placed:
                self.entities.append(clone)

        # Спавн противников
        self.spawn_enemies()

        # Обновляем камеру и видимую область
        self.update_camera()
        self.game_map.compute_fov(self.player.x, self.player.y, self.player.stats.vision_range)

        self.message_log.add(f"Уровень {self.current_level}: {LEVEL_NAMES.get(self.current_level, 'Неизвестно')}", YELLOW)

    def spawn_enemies(self):
        num_enemies = 4 + self.current_level * 2

        # Вес противников в зависимости от уровня
        if self.current_level <= 3:  # Кровеносная система
            weights = [
                (EntityType.NEUTROPHIL, 0.5),
                (EntityType.MACROPHAGE, 0.3),
                (EntityType.B_CELL, 0.2),
            ]
        elif self.current_level <= 6:  # Лимфатическая система
            weights = [
                (EntityType.B_CELL, 0.3),
                (EntityType.T_CELL, 0.3),
                (EntityType.NEUTROPHIL, 0.2),
                (EntityType.DENDRITIC, 0.2),
            ]
        elif self.current_level <= 9:  # Легкие
            weights = [
                (EntityType.DENDRITIC, 0.3),
                (EntityType.MACROPHAGE, 0.3),
                (EntityType.MAST_CELL, 0.2),
                (EntityType.T_CELL, 0.2),
            ]
        elif self.current_level <= 12:  # Печень
            weights = [
                (EntityType.MACROPHAGE, 0.4),
                (EntityType.T_CELL, 0.3),
                (EntityType.MAST_CELL, 0.3),
            ]
        else:  # Мозг
            weights = [
                (EntityType.T_CELL, 0.3),
                (EntityType.B_CELL, 0.3),
                (EntityType.DENDRITIC, 0.2),
                (EntityType.MACROPHAGE, 0.2),
            ]

        positions = self.game_map.get_enemy_spawn_positions(num_enemies, self.entities)

        for x, y in positions:
            # Выбор типа противника
            roll = random.random()
            cumulative = 0
            chosen_type = weights[0][0]

            for etype, weight in weights:
                cumulative += weight
                if roll <= cumulative:
                    chosen_type = etype
                    break

            enemy = self.create_enemy(chosen_type, x, y)
            self.entities.append(enemy)

    def create_enemy(self, entity_type: EntityType, x: int, y: int) -> Entity:
        level_bonus = self.current_level - 1

        configs = {
            EntityType.MACROPHAGE: {
                "stats": Stats(
                    hp=80 + level_bonus * 10,
                    max_hp=80 + level_bonus * 10,
                    attack=8 + level_bonus,
                    defense=8 + level_bonus,
                    speed=3,
                    vision_range=5
                ),
                "name": "Макрофаг",
                "color": PURPLE,
                "char": "M"
            },
            EntityType.NEUTROPHIL: {
                "stats": Stats(
                    hp=40 + level_bonus * 5,
                    max_hp=40 + level_bonus * 5,
                    attack=12 + level_bonus,
                    defense=3 + level_bonus // 2,
                    speed=12,
                    vision_range=6
                ),
                "name": "Нейтрофил",
                "color": ORANGE,
                "char": "N"
            },
            EntityType.B_CELL: {
                "stats": Stats(
                    hp=35 + level_bonus * 4,
                    max_hp=35 + level_bonus * 4,
                    attack=15 + level_bonus,
                    defense=2 + level_bonus // 2,
                    speed=6,
                    vision_range=8
                ),
                "name": "B-клетка",
                "color": BLUE,
                "char": "B"
            },
            EntityType.T_CELL: {
                "stats": Stats(
                    hp=50 + level_bonus * 6,
                    max_hp=50 + level_bonus * 6,
                    attack=20 + level_bonus * 2,
                    defense=4 + level_bonus // 2,
                    speed=8,
                    vision_range=5
                ),
                "name": "T-клетка",
                "color": RED,
                "char": "T"
            },
            EntityType.DENDRITIC: {
                "stats": Stats(
                    hp=30 + level_bonus * 3,
                    max_hp=30 + level_bonus * 3,
                    attack=5 + level_bonus // 2,
                    defense=2 + level_bonus // 2,
                    speed=5,
                    vision_range=10
                ),
                "name": "Дендритная клетка",
                "color": YELLOW,
                "char": "D"
            },
            EntityType.MAST_CELL: {
                "stats": Stats(
                    hp=45 + level_bonus * 5,
                    max_hp=45 + level_bonus * 5,
                    attack=8 + level_bonus,
                    defense=5 + level_bonus // 2,
                    speed=4,
                    vision_range=6
                ),
                "name": "Тучная клетка",
                "color": CYAN,
                "char": "*"
            },
        }

        config = configs.get(entity_type, configs[EntityType.NEUTROPHIL])

        return Entity(
            x=x, y=y,
            entity_type=entity_type,
            stats=config["stats"],
            name=config["name"],
            color=config["color"],
            char=config["char"]
        )

    def update_camera(self):
        view_width = SCREEN_WIDTH // TILE_SIZE
        view_height = (SCREEN_HEIGHT - 150) // TILE_SIZE

        self.camera_x = self.player.x - view_width // 2
        self.camera_y = self.player.y - view_height // 2

        self.camera_x = max(0, min(self.camera_x, self.game_map.width - view_width))
        self.camera_y = max(0, min(self.camera_y, self.game_map.height - view_height))

    def handle_input(self, key: int) -> str:
        if self.state == GameState.GAME_OVER or self.state == GameState.VICTORY:
            if key == arcade.key.R:
                self.init_new_game()
            elif key == arcade.key.ESCAPE:
                return "menu"
            return ""

        if self.state == GameState.LEVEL_UP:
            if key in [arcade.key.NUM_1, arcade.key.NUM_2, arcade.key.NUM_3]:
                idx = key - arcade.key.NUM_1
                if idx < len(self.available_mutations):
                    mutation = self.available_mutations[idx]
                    mutation.apply(self.player, self.resources)
                    self.message_log.add(f"Мутация: {mutation.name}", GREEN)
                    self.state = GameState.PLAYER_TURN
            return ""

        if self.state == GameState.PAUSED:
            if key == arcade.key.ESCAPE:
                self.state = GameState.PLAYER_TURN
            elif key == arcade.key.Q:
                return "menu"
            return ""

        if self.state != GameState.PLAYER_TURN:
            return ""

        dx, dy = 0, 0
        turn_taken = False

        if key == arcade.key.UP or key == arcade.key.W:
            dy = 1  # Было "-1", теперь "1" (персонаж движется вверх)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            dy = -1  # Было "1", теперь "-1" (персонаж движется вниз)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            dx = -1
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            dx = 1
        elif key == arcade.key.SPACE:
            # Пауза
            self.resources.atp = min(self.resources.max_atp, self.resources.atp + 5)
            self.message_log.add("Ожидание... +5 ATP", GREEN)
            turn_taken = True
        elif key == arcade.key.C:
            turn_taken = self.create_clone()
        elif key == arcade.key.E:
            turn_taken = self.try_use_exit()
        elif key == arcade.key.ESCAPE:
            self.state = GameState.PAUSED

        if dx != 0 or dy != 0:
            turn_taken = self.player_move_or_attack(dx, dy)

        if turn_taken:
            self.update_camera()
            self.game_map.compute_fov(self.player.x, self.player.y, self.player.stats.vision_range)
            self.state = GameState.ENEMY_TURN

        return ""

    def player_move_or_attack(self, dx: int, dy: int) -> bool:
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        # Проверка наличия существа на целевой позиции
        target = self.game_map.get_entity_at(new_x, new_y, self.entities)

        if target and target != self.player:
            # Проверка, является ли существо врагом (не клон)
            if target.entity_type != EntityType.VIRUS_CLONE:
                return self.attack(self.player, target)
            else:
                # Меняем позиции с клоном
                target.x, target.y = self.player.x, self.player.y
                self.player.x, self.player.y = new_x, new_y
                self.message_log.add("Поменялись местами с клоном", WHITE)
                return True

        elif self.game_map.is_walkable(new_x, new_y):
            # Перемещение
            self.player.x = new_x
            self.player.y = new_y
            self.resources.atp = max(0, self.resources.atp - 1)

            # Сбор ресурсов на кровяных сосудах
            if self.game_map.tiles[new_x][new_y] == TileType.BLOOD_VESSEL:
                if random.random() < 0.3:
                    gain = random.randint(5, 15)
                    self.resources.atp = min(self.resources.max_atp, self.resources.atp + gain)
                    self.message_log.add(f"+{gain} ATP из кровотока", GREEN)

            # Проверка повреждений
            damage = self.game_map.get_damage_at(new_x, new_y)
            if damage > 0:
                actual = self.player.take_damage(damage)
                self.message_log.add(f"Токсичная зона: -{actual} HP!", RED)

            return True

        return False

    def attack(self, attacker: Entity, defender: Entity) -> bool:
        damage = attacker.stats.attack + random.randint(-2, 2)
        actual_damage = defender.take_damage(damage)

        if attacker == self.player or attacker.entity_type == EntityType.VIRUS_CLONE:
            self.message_log.add(f"Атака на {defender.name}: -{actual_damage} HP", WHITE)
            self.resources.atp = max(0, self.resources.atp - 2)

            if not defender.is_alive:
                self.on_enemy_killed(defender)
        else:
            if defender == self.player:
                self.message_log.add(f"{attacker.name} атакует: -{actual_damage} HP", RED)
            else:
                self.message_log.add(f"{attacker.name} бьёт клона: -{actual_damage}", ORANGE)

        return True

    def on_enemy_killed(self, enemy: Entity):
        self.message_log.add(f"{enemy.name} уничтожен!", GREEN)

        # Получение ресурсов
        protein_gain = random.randint(8, 18)
        rna_gain = random.randint(2, 6)

        self.resources.protein = min(self.resources.max_protein, self.resources.protein + protein_gain)
        self.resources.rna = min(self.resources.max_rna, self.resources.rna + rna_gain)

        self.message_log.add(f"+{protein_gain} белка, +{rna_gain} РНК", CYAN)

        # Проверка на эволюцию
        if self.resources.rna >= 20:
            self.resources.rna -= 20
            self.trigger_evolution()

    def trigger_evolution(self):
        self.available_mutations = random.sample(MUTATIONS, min(3, len(MUTATIONS)))
        self.state = GameState.LEVEL_UP
        self.message_log.add("ЭВОЛЮЦИЯ! Выберите мутацию (1-3)", YELLOW)

    def create_clone(self) -> bool:
        if self.resources.protein < 30:
            self.message_log.add("Нужно 30 белка для клона", RED)
            return False

        # Поиск свободного соседнего места
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            x, y = self.player.x + dx, self.player.y + dy
            if self.game_map.is_walkable(x, y) and not self.game_map.is_blocked(x, y, self.entities):
                clone = Entity(
                    x=x, y=y,
                    entity_type=EntityType.VIRUS_CLONE,
                    stats=Stats(
                        hp=self.player.stats.max_hp // 2,
                        max_hp=self.player.stats.max_hp // 2,
                        attack=self.player.stats.attack - 2,
                        defense=self.player.stats.defense - 2,
                        speed=self.player.stats.speed,
                        vision_range=4
                    ),
                    name="Клон",
                    color=(100, 200, 100),
                    char="v"
                )
                self.virus_clones.append(clone)
                self.entities.append(clone)
                self.resources.protein -= 30
                self.message_log.add("Клон создан!", GREEN)
                return True

        self.message_log.add("Нет места для клона", RED)
        return False

    def try_use_exit(self) -> bool:
        if not self.game_map.exit_pos:
            return False

        # Проверка нахождения игрока на выходе
        if (self.player.x, self.player.y) != self.game_map.exit_pos:
            self.message_log.add("Найдите выход (зелёный >)", YELLOW)
            return False

        # Проверка уничтожения всех врагов
        enemies_alive = sum(1 for e in self.entities
                          if e.is_alive and e.entity_type not in [EntityType.PLAYER, EntityType.VIRUS_CLONE])

        if enemies_alive > 0:
            self.message_log.add(f"Осталось врагов: {enemies_alive}", RED)
            return False

        # Переход на следующий уровень
        self.current_level += 1

        if self.current_level > MAX_LEVEL:
            self.state = GameState.VICTORY
            self.message_log.add("ПОБЕДА! Организм захвачен!", GREEN)
        else:
            self.generate_level()

        return True

    def process_enemy_turn(self):
        for entity in self.entities:
            if not entity.is_alive:
                continue
            if entity.entity_type in [EntityType.PLAYER, EntityType.VIRUS_CLONE]:
                continue

            self.process_enemy_ai(entity)

        # Обрабатываем AI клонов
        for clone in self.virus_clones:
            if clone.is_alive:
                self.process_clone_ai(clone)

        # Обновляем зоны повреждения
        self.game_map.update_damage_zones()

        # Наносим урон зоне поражения игроку
        damage = self.game_map.get_damage_at(self.player.x, self.player.y)
        if damage > 0:
            actual = self.player.take_damage(damage)
            self.message_log.add(f"Токсин: -{actual} HP!", RED)

        # Проверка смерти игрока
        if not self.player.is_alive:
            self.state = GameState.GAME_OVER
            self.message_log.add("ВЫ ПОГИБЛИ!", RED)
            return

        self.turn_count += 1

        # Пополнение энергии пассивно
        self.resources.atp = min(self.resources.max_atp, self.resources.atp + 2)

        self.state = GameState.PLAYER_TURN

    def process_enemy_ai(self, enemy: Entity):
        # Нахождение ближайшего врага
        targets = [self.player] + [c for c in self.virus_clones if c.is_alive]

        if not targets:
            return

        closest = min(targets, key=lambda t: enemy.distance_to(t))
        dist = enemy.distance_to(closest)

        # Вне зоны видимости - случайное блуждание
        if dist > enemy.stats.vision_range:
            if random.random() < 0.3:
                dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                new_x, new_y = enemy.x + dx, enemy.y + dy
                if self.game_map.is_walkable(new_x, new_y) and not self.game_map.is_blocked(new_x, new_y, self.entities):
                    enemy.x, enemy.y = new_x, new_y
            return

        # Особые способности
        if enemy.entity_type == EntityType.B_CELL:
            # Атака издалека
            if 1 < dist <= 4:
                damage = enemy.stats.attack
                actual = closest.take_damage(damage)
                if closest == self.player:
                    self.message_log.add(f"B-клетка стреляет: -{actual} HP", RED)
                return

        elif enemy.entity_type == EntityType.DENDRITIC:
            # Призыв подкрепления
            if dist <= 6 and random.random() < 0.08:
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    x, y = enemy.x + dx, enemy.y + dy
                    if self.game_map.is_walkable(x, y) and not self.game_map.is_blocked(x, y, self.entities):
                        new_enemy = self.create_enemy(EntityType.NEUTROPHIL, x, y)
                        self.entities.append(new_enemy)
                        self.message_log.add("Дендритная клетка вызвала подкрепление!", YELLOW)
                        break
                return

        elif enemy.entity_type == EntityType.MAST_CELL:
            # Создание токсичной зоны
            if dist <= 5 and random.random() < 0.15:
                self.game_map.add_damage_zone(closest.x, closest.y, 5, 3)
                self.message_log.add("Тучная клетка создала токсичную зону!", ORANGE)
                return

        # Двигаемся к цели или атакуем
        if dist > 1.5:
            dx = 0 if closest.x == enemy.x else (1 if closest.x > enemy.x else -1)
            dy = 0 if closest.y == enemy.y else (1 if closest.y > enemy.y else -1)

            # Сначала горизонтально
            if dx != 0:
                new_x = enemy.x + dx
                if self.game_map.is_walkable(new_x, enemy.y) and not self.game_map.is_blocked(new_x, enemy.y, self.entities):
                    enemy.x = new_x
                    return

            # Затем вертикально
            if dy != 0:
                new_y = enemy.y + dy
                if self.game_map.is_walkable(enemy.x, new_y) and not self.game_map.is_blocked(enemy.x, new_y, self.entities):
                    enemy.y = new_y
                    return
        else:
            # Атака
            self.attack(enemy, closest)

    def process_clone_ai(self, clone: Entity):
        # Искусственный интеллект клонов
        enemies = [e for e in self.entities if e.is_alive and
                  e.entity_type not in [EntityType.PLAYER, EntityType.VIRUS_CLONE]]

        if not enemies:
            # Следуем за игроком
            dist = clone.distance_to(self.player)
            if dist > 3:
                dx = 0 if self.player.x == clone.x else (1 if self.player.x > clone.x else -1)
                dy = 0 if self.player.y == clone.y else (1 if self.player.y > clone.y else -1)

                if dx != 0:
                    new_x = clone.x + dx
                    if self.game_map.is_walkable(new_x, clone.y) and not self.game_map.is_blocked(new_x, clone.y, self.entities):
                        clone.x = new_x
                        return
                if dy != 0:
                    new_y = clone.y + dy
                    if self.game_map.is_walkable(clone.x, new_y) and not self.game_map.is_blocked(clone.x, new_y, self.entities):
                        clone.y = new_y
            return

        closest = min(enemies, key=lambda e: clone.distance_to(e))
        dist = clone.distance_to(closest)

        if dist <= 1.5:
            self.attack(clone, closest)
        else:
            dx = 0 if closest.x == clone.x else (1 if closest.x > clone.x else -1)
            dy = 0 if closest.y == clone.y else (1 if closest.y > clone.y else -1)

            if dx != 0:
                new_x = clone.x + dx
                if self.game_map.is_walkable(new_x, clone.y) and not self.game_map.is_blocked(new_x, clone.y, self.entities):
                    clone.x = new_x
                    return
            if dy != 0:
                new_y = clone.y + dy
                if self.game_map.is_walkable(clone.x, new_y) and not self.game_map.is_blocked(clone.x, new_y, self.entities):
                    clone.y = new_y

    def get_enemies_count(self) -> int:
        return sum(1 for e in self.entities
                   if e.is_alive and e.entity_type not in [EntityType.PLAYER, EntityType.VIRUS_CLONE])

    def render(self):
        self.screen.clear()

        # Отрисовка карты
        self.ui.render_map(self.game_map, self.entities, self.camera_x, self.camera_y, self.player)

        # Панель интерфейса
        self.ui.render_ui_panel(
            self.player, self.resources, self.message_log,
            self.current_level, self.turn_count, self.virus_clones,
            self.get_enemies_count()
        )

        # Полная карта сверху справа
        self.ui.render_fullmap(
            self.game_map, self.player, self.entities,
            SCREEN_WIDTH - 210, 10, 200, 150
        )

        # Наложения
        if self.state == GameState.LEVEL_UP:
            self.ui.render_evolution_menu(self.available_mutations)
        elif self.state == GameState.GAME_OVER:
            self.ui.render_game_over(self.current_level, self.turn_count)
        elif self.state == GameState.VICTORY:
            self.ui.render_victory(self.turn_count)
        elif self.state == GameState.PAUSED:
            self.ui.render_pause()

    def update(self):
        if self.state == GameState.ENEMY_TURN:
            self.process_enemy_turn()

import random
import math
import arcade
from constants import TileType, MAP_WIDTH, MAP_HEIGHT
from entities import Entity

from typing import List, Optional, Tuple, Dict


# Класс игровой карты с процедурной генерацией
class GameMap:
    def __init__(self, width: int = MAP_WIDTH, height: int = MAP_HEIGHT, level: int = 1):
        self.width = width
        self.height = height
        self.level = level
        self.tiles = [[TileType.WALL for _ in range(height)] for _ in range(width)]
        self.visible = [[False for _ in range(height)] for _ in range(width)]
        self.explored = [[False for _ in range(height)] for _ in range(width)]
        self.damage_zones: List[List] = []  # [x, y, damage, turns_left]
        self.rooms: List[tuple] = []        # (x, y, w, h)
        self.exit_pos: Optional[Tuple[int, int]] = None
        self.generate()

    # Генерация случайной карты с комнатами и коридорами
    def generate(self):
        self.rooms = []
        num_rooms = random.randint(8, 12)

        # Создание непересекающихся комнат
        for _ in range(num_rooms * 10):
            if len(self.rooms) >= num_rooms:
                break

            w = random.randint(6, 12)
            h = random.randint(6, 10)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)

            new_room = (x, y, w, h)

            # Проверка пересечения с другими комнатами
            overlaps = False
            for room in self.rooms:
                if self._rooms_collide(new_room, room):
                    overlaps = True
                    break

            if not overlaps:
                self.rooms.append(new_room)
                self._create_room(new_room)

        # Соединение комнат коридорами
        for i in range(len(self.rooms) - 1):
            center1 = self._room_center(self.rooms[i])
            center2 = self._room_center(self.rooms[i+1])
            self._create_corridor(center1, center2)

        # Добавление кровеносных сосудов на ранних уровнях
        if self.level <= 3:
            self._add_blood_vessels()

        # Установка выхода в последней комнате
        if self.rooms:
            last_room = self.rooms[-1]
            self.exit_pos = (last_room[0]+last_room[2]//2, last_room[1]+last_room[3]//2)
            self.tiles[self.exit_pos[0]][self.exit_pos[1]] = TileType.EXIT

    # Проверка пересечения двух комнат
    def _rooms_collide(self, room1: tuple, room2: tuple) -> bool:
        x1, y1, w1, h1 = room1
        x2, y2, w2, h2 = room2
        return (x1+w1 > x2 and x1 < x2+w2 and y1+h1 > y2 and y1 < y2+h2)

    # Получение центра комнаты
    def _room_center(self, room: tuple) -> tuple:
        x, y, w, h = room
        return (x+w//2, y+h//2)

    # Создание комнаты на карте
    def _create_room(self, room: tuple):
        x, y, w, h = room
        for xi in range(x, x+w):
            for yi in range(y, y+h):
                if 0 <= xi < self.width and 0 <= yi < self.height:
                    self.tiles[xi][yi] = TileType.FLOOR

    # Создание коридора между двумя точками
    def _create_corridor(self, pos1: tuple, pos2: tuple):
        x1, y1 = pos1
        x2, y2 = pos2

        # Случайный выбор направления
        if random.random() < 0.5:
            self._create_h_tunnel(x1, x2, y1)
            self._create_v_tunnel(y1, y2, x2)
        else:
            self._create_v_tunnel(y1, y2, x1)
            self._create_h_tunnel(x1, x2, y2)

    # Горизонтальный туннель
    def _create_h_tunnel(self, x1: int, x2: int, y: int):
        for x in range(min(x1, x2), max(x1, x2)+1):
            if 0 <= x < self.width and 0 <= y < self.height:
                if self.tiles[x][y] == TileType.WALL:
                    self.tiles[x][y] = TileType.FLOOR

    # Вертикальный туннель
    def _create_v_tunnel(self, y1: int, y2: int, x: int):
        for y in range(min(y1, y2), max(y1, y2)+1):
            if 0 <= x < self.width and 0 <= y < self.height:
                if self.tiles[x][y] == TileType.WALL:
                    self.tiles[x][y] = TileType.FLOOR

    # Добавление кровеносных сосудов
    def _add_blood_vessels(self):
        for room in self.rooms:
            if random.random() < 0.3:
                if random.random() < 0.5:
                    y = room[1] + room[3]//2
                    for x in range(room[0], room[0]+room[2]):
                        if self.tiles[x][y] == TileType.FLOOR:
                            self.tiles[x][y] = TileType.BLOOD_VESSEL
                else:
                    x = room[0] + room[2]//2
                    for y in range(room[1], room[1]+room[3]):
                        if self.tiles[x][y] == TileType.FLOOR:
                            self.tiles[x][y] = TileType.BLOOD_VESSEL

    # Проверка проходимости клетки
    def is_walkable(self, x: int, y: int) -> bool:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[x][y] != TileType.WALL
        return False

    # Проверка блокировки клетки сущностями
    def is_blocked(self, x: int, y: int, entities: List[Entity]) -> bool:
        if not self.is_walkable(x, y):
            return True
        for entity in entities:
            if entity.is_alive and entity.x == x and entity.y == y:
                return True
        return False

    # Получение сущности в указанной клетке
    def get_entity_at(self, x: int, y: int, entities: List[Entity]) -> Optional[Entity]:
        for entity in entities:
            if entity.is_alive and entity.x == x and entity.y == y:
                return entity
        return None

    # Расчет поля обзора из заданной точки
    def compute_fov(self, origin_x: int, origin_y: int, radius: int):
        for x in range(self.width):
            for y in range(self.height):
                self.visible[x][y] = False

        # Трассировка лучей по 360 градусам
        for angle in range(360):
            rad = math.radians(angle)
            dx = math.cos(rad)
            dy = math.sin(rad)

            x, y = float(origin_x), float(origin_y)

            for _ in range(radius):
                ix, iy = round(x), round(y)

                if 0 <= ix < self.width and 0 <= iy < self.height:
                    self.visible[ix][iy] = True
                    self.explored[ix][iy] = True

                    if self.tiles[ix][iy] == TileType.WALL:
                        break
                else:
                    break

                x += dx * 0.5
                y += dy * 0.5

    # Добавление зоны урона
    def add_damage_zone(self, x: int, y: int, damage: int, duration: int):
        self.damage_zones.append([x, y, damage, duration])

    # Обновление длительности зон урона
    def update_damage_zones(self):
        self.damage_zones = [[x, y, d, t - 1] for x, y, d, t in self.damage_zones if t > 1]

    # Получение урона в клетке от зон
    def get_damage_at(self, x: int, y: int) -> int:
        total = 0
        for zx, zy, damage, _ in self.damage_zones:
            if zx == x and zy == y:
                total += damage
        return total

    # Позиция спавна игрока (первая комната)
    def get_spawn_position(self) -> Tuple[int, int]:
        if self.rooms:
            room = self.rooms[0]
            return room[0]+room[2]//2, room[1]+room[3]//2
        return 5, 5

    # Позиции для спавна врагов
    def get_enemy_spawn_positions(self, count: int, entities: List[Entity]) -> List[Tuple[int, int]]:
        positions = []

        if len(self.rooms) <= 1:
            return positions

        for _ in range(count * 5):
            if len(positions) >= count:
                break

            room = random.choice(self.rooms[1:])

            for _ in range(10):
                x = random.randint(room[0]+1, room[0]+room[2]-2)
                y = random.randint(room[1]+1, room[1]+room[3]-2)

                if self.exit_pos and (x, y) == self.exit_pos:
                    continue

                if not self.is_blocked(x, y, entities):
                    # Проверка минимального расстояния между врагами
                    too_close = False
                    for px, py in positions:
                        if abs(px-x) <= 1 and abs(py-y) <= 1:
                            too_close = True
                            break

                    if not too_close:
                        positions.append((x, y))
                        break

        return positions

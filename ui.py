# ui.py
import arcade
from constants import *
from entities import Entity, Resources, Mutation
from game_map import GameMap

from collections import deque
from typing import List, Tuple, Deque


# Класс отвечающий за хранение и управление журналом сообщений игры
class MessageLog:
    def __init__(self, max_messages: int = 50):
        # Хранилище сообщений в виде очереди с ограниченной длиной
        self.messages: Deque[Tuple[str, Tuple[int, int, int]]] = deque(maxlen=max_messages)

    # Функция добавления нового сообщения в журнал
    # param text: Текст сообщения
    # param color: Цвет текста сообщения
    def add(self, text: str, color: Tuple[int, int, int] = WHITE):
        self.messages.append((text, color))

    # Функция получения последних сообщений из журнала
    # param count: Количество возвращаемых сообщений
    # return: Список последних сообщений
    def get_recent(self, count: int = 6) -> List[Tuple[str, Tuple[int, int, int]]]:
        return list(self.messages)[-count:]

    # Функция очистки журнала сообщений
    def clear(self):
        self.messages.clear()


# Класс отвечающий за графический интерфейс игры
class UI:
    def __init__(self, window: arcade.Window):
        self.window = window
        font_path = "a_BighausTitulBrk_ExtraBold.ttf"

        # Загружаем пользовательский шрифт
        arcade.load_font(font_path)
        self.font_name = "a_BighausTitulBrk ExtraBold"  # Имя шрифта без расширения .ttf

        # Размеры шрифтов для разных элементов интерфейса
        self.font_size = 16
        self.large_font_size = 32
        self.small_font_size = 12
        self.title_font_size = 48

    # Функция рисования залитого прямоугольника от левого нижнего угла
    # param x: X координата левого нижнего угла
    # param y: Y координата левого нижнего угла
    # param width: Ширина прямоугольника
    # param height: Высота прямоугольника
    # param color: Цвет заливки
    def draw_lbwh_rectangle_filled(self, x, y, width, height, color):
        # Конвертация координат для Arcade (лево-право-низ-верх)
        left = x
        right = x + width
        bottom = y
        top = y + height
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)

    # Функция рисования контура прямоугольника от левого нижнего угла
    # param x: X координата левого нижнего угла
    # param y: Y координата левого нижнего угла
    # param width: Ширина прямоугольника
    # param height: Высота прямоугольника
    # param color: Цвет контура
    # param border_width: Толщина линии контура
    def draw_lbwh_rectangle_outline(self, x, y, width, height, color, border_width):
        # Конвертация координат для Arcade
        left = x
        right = x + width
        bottom = y
        top = y + height
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, color, border_width)

    # Функция отрисовки игровой карты с сущностями
    # param game_map: Объект карты игры
    # param entities: Список сущностей на карте
    # param camera_x: X координата камеры
    # param camera_y: Y координата камеры
    # param player: Объект игрока
    def render_map(self, game_map: GameMap, entities: List[Entity],
                   camera_x: int, camera_y: int, player: Entity):
        # Вычисление размеров видимой области в тайлах
        view_width = SCREEN_WIDTH // TILE_SIZE
        view_height = (SCREEN_HEIGHT - 150) // TILE_SIZE

        # Отрисовка тайлов карты
        for screen_x in range(view_width):
            for screen_y in range(view_height):
                map_x = screen_x + camera_x
                map_y = screen_y + camera_y

                if 0 <= map_x < game_map.width and 0 <= map_y < game_map.height:
                    pixel_x = screen_x * TILE_SIZE
                    pixel_y = screen_y * TILE_SIZE

                    tile = game_map.tiles[map_x][map_y]
                    visible = game_map.visible[map_x][map_y]
                    explored = game_map.explored[map_x][map_y]

                    # Отрисовка видимых тайлов
                    if visible:
                        # Определение цвета тайла в зависимости от его типа
                        if tile == TileType.WALL:
                            color = (60, 30, 40)
                        elif tile == TileType.FLOOR:
                            color = (30, 20, 25)
                        elif tile == TileType.BLOOD_VESSEL:
                            color = (80, 20, 30)
                        elif tile == TileType.EXIT:
                            color = (40, 80, 40)
                        else:
                            color = (30, 20, 25)

                        self.draw_lbwh_rectangle_filled(pixel_x, pixel_y, TILE_SIZE, TILE_SIZE, color)

                        # Отметка выхода с уровня
                        if tile == TileType.EXIT:
                            # Рамка выхода
                            self.draw_lbwh_rectangle_outline(pixel_x + 4, pixel_y + 4,
                                                             TILE_SIZE - 8, TILE_SIZE - 8, GREEN, 2)
                            # Символ выхода
                            arcade.draw_text(">",
                                             pixel_x + TILE_SIZE // 2,
                                             pixel_y + TILE_SIZE // 2,
                                             GREEN, self.small_font_size,
                                             anchor_x="center", anchor_y="center",
                                             font_name=self.font_name)

                        # Отображение зон нанесения урона
                        for zx, zy, _, _ in game_map.damage_zones:
                            if zx == map_x and zy == map_y:
                                self.draw_lbwh_rectangle_outline(pixel_x + 2, pixel_y + 2,
                                                                 TILE_SIZE - 4, TILE_SIZE - 4,
                                                                 (100, 50, 0), 2)

                    # Отрисовка исследованных тайлов
                    elif explored:
                        color = (20, 15, 18)
                        self.draw_lbwh_rectangle_filled(pixel_x, pixel_y, TILE_SIZE, TILE_SIZE, color)

        # Отрисовка сущностей на карте
        for entity in entities:
            if not entity.is_alive:
                continue

            screen_x = (entity.x - camera_x) * TILE_SIZE
            screen_y = (entity.y - camera_y) * TILE_SIZE

            if 0 <= entity.x < game_map.width and 0 <= entity.y < game_map.height:
                # Показываем сущность только если она видима или это игрок
                if game_map.visible[entity.x][entity.y] or entity == player:
                    # Фон для сущности
                    self.draw_lbwh_rectangle_filled(screen_x + 4, screen_y + 4,
                                                    TILE_SIZE - 8, TILE_SIZE - 8, entity.color)

                    # Символ сущности
                    arcade.draw_text(entity.char,
                                     screen_x + TILE_SIZE // 2,
                                     screen_y + TILE_SIZE // 2,
                                     BLACK, self.font_size,
                                     anchor_x="center", anchor_y="center",
                                     font_name=self.font_name)

                    # Полоска здоровья для врагов
                    if entity != player and entity.entity_type != EntityType.VIRUS_CLONE:
                        hp_ratio = entity.stats.hp / entity.stats.max_hp
                        bar_width = TILE_SIZE - 8
                        self.draw_lbwh_rectangle_filled(screen_x + 4, screen_y + TILE_SIZE - 12,
                                                        bar_width, 3, DARK_RED)
                        self.draw_lbwh_rectangle_filled(screen_x + 4, screen_y + TILE_SIZE - 12,
                                                        int(bar_width * hp_ratio), 3, RED)

    # Функция отрисовки панели интерфейса внизу экрана
    # param player: Объект игрока
    # param resources: Ресурсы игрока
    # param message_log: Журнал сообщений
    # param current_level: Текущий уровень
    # param turn_count: Счетчик ходов
    # param virus_clones: Список клонов вируса
    # param enemies_count: Количество врагов
    def render_ui_panel(self, player: Entity, resources: Resources, message_log: MessageLog,
                        current_level: int, turn_count: int, virus_clones: list,
                        enemies_count: int):
        ui_y = SCREEN_HEIGHT - 145

        # Фон панели интерфейса
        self.draw_lbwh_rectangle_filled(0, ui_y, SCREEN_WIDTH, 145, (20, 15, 20))
        arcade.draw_line(0, ui_y, SCREEN_WIDTH, ui_y, GRAY)

        # Полоски здоровья и АТФ
        self._render_bar(10, ui_y + 10, 200, 20, player.stats.hp, player.stats.max_hp, RED, DARK_RED, "HP")
        self._render_bar(10, ui_y + 35, 200, 20, resources.atp, resources.max_atp, GREEN, DARK_GREEN, "ATP")

        # Отображение ресурсов
        arcade.draw_text(f"Белок: {resources.protein}/{resources.max_protein}",
                         10, ui_y + 60, CYAN, self.font_size, font_name=self.font_name)
        arcade.draw_text(f"РНК: {resources.rna}/{resources.max_rna}",
                         10, ui_y + 80, PURPLE, self.font_size, font_name=self.font_name)

        # Статистика игрока
        stats_x = 230
        arcade.draw_text(f"АТК: {player.stats.attack}", stats_x, ui_y + 10,
                         WHITE, self.small_font_size, font_name=self.font_name)
        arcade.draw_text(f"ЗАЩ: {player.stats.defense}", stats_x, ui_y + 28,
                         WHITE, self.small_font_size, font_name=self.font_name)
        arcade.draw_text(f"СКР: {player.stats.speed}", stats_x, ui_y + 46,
                         WHITE, self.small_font_size, font_name=self.font_name)
        arcade.draw_text(f"ОБЗ: {player.stats.vision_range}", stats_x, ui_y + 64,
                         WHITE, self.small_font_size, font_name=self.font_name)

        # Информация об уровне и ходе
        arcade.draw_text(f"Уровень: {current_level}/13", stats_x, ui_y + 85,
                         YELLOW, self.font_size, font_name=self.font_name)
        arcade.draw_text(f"Ход: {turn_count}", stats_x, ui_y + 105,
                         GRAY, self.small_font_size, font_name=self.font_name)

        # Количество клонов и врагов
        clones_count = len([c for c in virus_clones if c.is_alive])
        arcade.draw_text(f"Клоны: {clones_count}", stats_x + 80, ui_y + 105,
                         GREEN, self.small_font_size, font_name=self.font_name)
        arcade.draw_text(f"Враги: {enemies_count}", stats_x, ui_y + 120,
                         RED, self.small_font_size, font_name=self.font_name)

        # Журнал сообщений
        log_x = 380
        messages = message_log.get_recent(6)
        for i, (text, color) in enumerate(messages):
            arcade.draw_text(text[:55], log_x, ui_y + 10 + i * 18,
                             color, self.small_font_size, font_name=self.font_name)

        # Подсказка по управлению
        controls = "WASD: передвижение | SPACE: ожидание | C: клонирование | E: выход | ESC: пауза"
        arcade.draw_text(controls, log_x, ui_y + 125, GRAY, self.small_font_size, font_name=self.font_name)

    # Функция отрисовки полоски с показателем
    # param x: X координата левого нижнего угла полоски
    # param y: Y координата левого нижнего угла полоски
    # param width: Ширина полоски
    # param height: Высота полоски
    # param value: Текущее значение
    # param max_value: Максимальное значение
    # param fg_color: Цвет заполненной части
    # param bg_color: Цвет фона
    # param label: Надпись полоски
    def _render_bar(self, x: int, y: int, width: int, height: int,
                    value: int, max_value: int, fg_color, bg_color, label: str):
        # Фон полоски
        self.draw_lbwh_rectangle_filled(x, y, width, height, bg_color)
        # Заполненная часть
        bar_width = int(width * (value / max_value)) if max_value > 0 else 0
        self.draw_lbwh_rectangle_filled(x, y, bar_width, height, fg_color)
        # Контур полоски
        self.draw_lbwh_rectangle_outline(x, y, width, height, WHITE, 1)

        # Текст с значениями
        arcade.draw_text(f"{label}: {value}/{max_value}",
                         x + width // 2, y + height // 2,
                         WHITE, self.small_font_size,
                         anchor_x="center", anchor_y="center",
                         font_name=self.font_name)

    # Функция отрисовки мини-карты
    # param game_map: Объект карты игры
    # param player: Объект игрока
    # param entities: Список сущностей
    # param x: X координата левого нижнего угла мини-карты
    # param y: Y координата левого нижнего угла мини-карты
    # param width: Ширина мини-карты
    # param height: Высота мини-карты
    def render_fullmap(self, game_map: GameMap, player: Entity, entities: List[Entity],
                       x: int, y: int, width: int, height: int):
        # Фон мини-карты
        self.draw_lbwh_rectangle_filled(x, y, width, height, (20, 15, 20))
        self.draw_lbwh_rectangle_outline(x, y, width, height, GRAY, 1)

        # Коэффициенты масштабирования
        scale_x = width / game_map.width
        scale_y = height / game_map.height

        # Поиск комнаты, в которой находится игрок
        player_room = None
        for room in game_map.rooms:
            # Обработка разных форматов комнат
            if isinstance(room, tuple):
                if len(room) >= 4:
                    left, top, right, bottom = room[:4]
                    if left <= player.x < right and top <= player.y < bottom:
                        player_room = room
                        break
            elif hasattr(room, 'contains'):
                if room.contains(player.x, player.y):
                    player_room = room
                    break
            elif hasattr(room, 'left') and hasattr(room, 'right') and hasattr(room, 'top') and hasattr(room, 'bottom'):
                if room.left <= player.x < room.right and room.top <= player.y < room.bottom:
                    player_room = room
                    break

        # Отрисовка комнат на мини-карте
        for room in game_map.rooms:
            # Получение границ комнаты
            if isinstance(room, tuple):
                if len(room) >= 4:
                    left, top, right, bottom = room[:4]
                else:
                    continue
            elif hasattr(room, 'left') and hasattr(room, 'right') and hasattr(room, 'top') and hasattr(room, 'bottom'):
                left = room.left
                top = room.top
                right = room.right
                bottom = room.bottom
            else:
                continue

            # Расчет координат комнаты на мини-карте
            rx = x + int(left * scale_x)
            ry = y + int(top * scale_y)
            rw = max(2, int((right - left) * scale_x))
            rh = max(2, int((bottom - top) * scale_y))

            # Определение цвета комнаты
            if room == player_room:
                room_color = (60, 80, 60)
                border_color = GREEN
            elif any(game_map.explored[tx][ty]
                     for tx in range(left, min(right, game_map.width))
                     for ty in range(top, min(bottom, game_map.height))):
                room_color = (45, 40, 50)
                border_color = (80, 70, 90)
            else:
                room_color = (25, 22, 28)
                border_color = (40, 35, 45)

            self.draw_lbwh_rectangle_filled(rx, ry, rw, rh, room_color)
            self.draw_lbwh_rectangle_outline(rx, ry, rw, rh, border_color, 1)

        # Отрисовка коридоров на мини-карте
        for mx in range(game_map.width):
            for my in range(game_map.height):
                if game_map.explored[mx][my]:
                    tile = game_map.tiles[mx][my]
                    if tile != TileType.WALL:
                        # Проверка, находится ли тайл в комнате
                        in_room = False
                        for room in game_map.rooms:
                            if isinstance(room, tuple) and len(room) >= 4:
                                left, top, right, bottom = room[:4]
                                if left <= mx < right and top <= my < bottom:
                                    in_room = True
                                    break
                            elif hasattr(room, 'contains'):
                                if room.contains(mx, my):
                                    in_room = True
                                    break
                            elif hasattr(room, 'left') and hasattr(room, 'right') and hasattr(room, 'top') and hasattr(
                                    room, 'bottom'):
                                if room.left <= mx < room.right and room.top <= my < room.bottom:
                                    in_room = True
                                    break

                        # Отрисовка коридора
                        if not in_room:
                            px = x + int(mx * scale_x)
                            py = y + int(my * scale_y)
                            self.draw_lbwh_rectangle_filled(px, py,
                                                            max(1, int(scale_x)),
                                                            max(1, int(scale_y)),
                                                            (50, 45, 55))

        # Отрисовка выхода на мини-карте
        if game_map.exit_pos:
            ex = x + int(game_map.exit_pos[0] * scale_x)
            ey = y + int(game_map.exit_pos[1] * scale_y)
            arcade.draw_lbwh_rectangle_filled(ex + 2, ey + 2, 4, 4, GREEN)

        # Отрисовка врагов на мини-карте
        for entity in entities:
            if entity.is_alive and entity != player and entity.entity_type != EntityType.VIRUS_CLONE:
                if game_map.visible[entity.x][entity.y]:
                    ex = x + int(entity.x * scale_x)
                    ey = y + int(entity.y * scale_y)
                    arcade.draw_lbwh_rectangle_filled(ex + 1.5, ey + 1.5, 3, 3, RED)

        # Отрисовка клонов на мини-карте
        for entity in entities:
            if entity.is_alive and entity.entity_type == EntityType.VIRUS_CLONE:
                cx = x + int(entity.x * scale_x)
                cy = y + int(entity.y * scale_y)
                arcade.draw_lbwh_rectangle_filled(cx + 1, cy + 1, 2, 2, (100, 200, 100))

        # Отрисовка игрока на мини-карте
        px = x + int(player.x * scale_x)
        py = y + int(player.y * scale_y)
        arcade.draw_lbwh_rectangle_filled(px + 2.5, py + 2.5, 5, 5, GREEN)
        arcade.draw_lbwh_rectangle_outline(px + 2.5, py + 2.5, 5, 5, WHITE, 1)

        # Подсчет исследованных комнат
        explored_rooms = 0
        for room in game_map.rooms:
            if isinstance(room, tuple) and len(room) >= 4:
                left, top, right, bottom = room[:4]
            elif hasattr(room, 'left') and hasattr(room, 'right') and hasattr(room, 'top') and hasattr(room, 'bottom'):
                left = room.left
                top = room.top
                right = room.right
                bottom = room.bottom
            else:
                continue

            if any(game_map.explored[tx][ty]
                   for tx in range(left, min(right, game_map.width))
                   for ty in range(top, min(bottom, game_map.height))):
                explored_rooms += 1

        # Отображение статистики комнат
        arcade.draw_text(f"Комнат: {explored_rooms}/{len(game_map.rooms)}",
                         x + 3, y + height - 18,
                         GRAY, self.small_font_size, font_name=self.font_name)

    # Функция отрисовки меню выбора мутаций
    # param mutations: Список доступных мутаций
    def render_evolution_menu(self, mutations: list):
        # Затемнение фона
        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                     SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 180))

        # Заголовок меню
        arcade.draw_text("ЭВОЛЮЦИЯ", SCREEN_WIDTH // 2, 100,
                         GREEN, self.large_font_size,
                         anchor_x="center", font_name=self.font_name)

        arcade.draw_text("Выберите мутацию (нажмите 1, 2 или 3)",
                         SCREEN_WIDTH // 2, 150, WHITE, self.font_size,
                         anchor_x="center", font_name=self.font_name)

        # Отрисовка вариантов мутаций
        for i, mutation in enumerate(mutations):
            y_pos = 220 + i * 100
            box_x = SCREEN_WIDTH // 2 - 200
            box_y = y_pos
            box_width = 400
            box_height = 80

            # Фон для варианта мутации
            self.draw_lbwh_rectangle_filled(box_x, box_y, box_width, box_height, (40, 35, 40))
            self.draw_lbwh_rectangle_outline(box_x, box_y, box_width, box_height, GREEN, 2)

            # Номер варианта
            arcade.draw_text(str(i + 1), box_x + 20, box_y + 20,
                             GREEN, self.large_font_size, font_name=self.font_name)

            # Название мутации
            arcade.draw_text(mutation.name, box_x + 70, box_y + 15,
                             WHITE, self.font_size, font_name=self.font_name)

            # Описание мутации
            arcade.draw_text(mutation.description, box_x + 70, box_y + 45,
                             GRAY, self.small_font_size, font_name=self.font_name)

    # Функция отрисовки экрана поражения
    # param current_level: Текущий уровень
    # param turn_count: Количество ходов
    def render_game_over(self, current_level: int, turn_count: int):
        # Затемнение фона
        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                     SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 200))

        # Сообщение о поражении
        arcade.draw_text("ВИРУС УНИЧТОЖЕН", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                         RED, self.large_font_size, anchor_x="center", font_name=self.font_name)

        # Статистика игры
        arcade.draw_text(f"Уровень: {current_level} | Ходы: {turn_count}",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20,
                         WHITE, self.font_size, anchor_x="center", font_name=self.font_name)

        # Подсказки по управлению
        arcade.draw_text("R - перезапуск | ESC - меню",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70,
                         YELLOW, self.font_size, anchor_x="center", font_name=self.font_name)

    # Функция отрисовки экрана победы
    # param turn_count: Количество ходов
    def render_victory(self, turn_count: int):
        # Затемнение фона
        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                     SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 200))

        # Сообщение о победе
        arcade.draw_text("ПОБЕДА!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                         GREEN, self.large_font_size, anchor_x="center", font_name=self.font_name)

        arcade.draw_text("Вы захватили контроль над организмом!",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                         CYAN, self.font_size, anchor_x="center", font_name=self.font_name)

        # Статистика игры
        arcade.draw_text(f"Ходы: {turn_count}",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40,
                         WHITE, self.font_size, anchor_x="center", font_name=self.font_name)

        # Подсказки по управлению
        arcade.draw_text("R - новая игра | ESC - меню",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90,
                         YELLOW, self.font_size, anchor_x="center", font_name=self.font_name)

    # Функция отрисовки экрана паузы
    def render_pause(self):
        # Затемнение фона
        arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                     SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 180))

        # Сообщение о паузе
        arcade.draw_text("ПАУЗА", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                         WHITE, self.large_font_size, anchor_x="center", font_name=self.font_name)

        # Подсказки по управлению
        arcade.draw_text("ESC - продолжение | Q - в меню",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20,
                         GRAY, self.font_size, anchor_x="center", font_name=self.font_name)
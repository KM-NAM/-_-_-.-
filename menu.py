import arcade
from constants import *


# Класс отвечающий за главное меню игры
class Menu:
    def __init__(self, screen: arcade.View):
        self.screen = screen
        # Шрифты для меню
        self.font = ":resources:fonts/calibri.ttf"
        self.large_font = ":resources:fonts/calibri.ttf"
        self.small_font = ":resources:fonts/calibri.ttf"
        self.title_font = ":resources:fonts/calibri.ttf"
        # Строки в меню
        self.menu_items = ["Начать игру", "Руководство", "Выход"]
        self.selected_item = 0
        self.guide_scroll = 0

    # Функция отвечающая за обработку нажатий клавиш в меню: param key: Нажатая клавиша,
    # return: Действие ('start', 'guide', 'quit'), если выбрано действие.
    def handle_input(self, key: int) -> str:
        if key == arcade.key.UP or key == arcade.key.W:
            self.selected_item = (self.selected_item - 1) % len(self.menu_items)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.selected_item = (self.selected_item + 1) % len(self.menu_items)
        elif key == arcade.key.RETURN or key == arcade.key.SPACE:
            if self.selected_item == 0:
                return "start"
            elif self.selected_item == 1:
                return "guide"
            elif self.selected_item == 2:
                return "quit"
        return ""

    # Функция отвечающая за обработку нажатий клавиш в "руководстве"
    def handle_guide_input(self, key: int) -> bool:
        if key == arcade.key.ESCAPE or key == arcade.key.RETURN:
            self.guide_scroll = 0
            return True
        elif key == arcade.key.UP or key == arcade.key.W:
            self.guide_scroll = max(0, self.guide_scroll - 30)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.guide_scroll = min(800, self.guide_scroll + 30)
        return False

    # Функция отвечающая за отрисовку меню
    def render_main_menu(self):
        self.background = arcade.load_texture("background1.png")
        arcade.draw_texture_rect(self.background, arcade.LBWH(0, 0, 1280, 720))
        # Титульный текст
        arcade.draw_text("L.A.T.E.N.D", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 270, GREEN, font_size=96,
                         anchor_x="center", anchor_y="center", font_name=self.title_font)
        for index, item in enumerate(reversed(self.menu_items)):
            y = SCREEN_HEIGHT // 2 + (index - 1) * 60
            selected = (len(self.menu_items) - 1 - index) == self.selected_item
            color = GREEN if selected else GRAY
            text = f"> {item}" if selected else f"  {item}"
            arcade.draw_text(text, SCREEN_WIDTH // 6.5, y - 250, color, font_size=32, anchor_x="center", anchor_y="center",
                             font_name=self.font)
        arcade.draw_text("v1.0", SCREEN_WIDTH - 100, 60, (50, 50, 50), font_size=20, anchor_x="right",
                         anchor_y="bottom", font_name=self.small_font)

    # Функция отвечающая за отрисовку "руководства"
    def render_guide(self):
        self.screen.clear((15, 10, 15))
        # Содержание окна
        guide_content = [
            ("КОНЦЕПЦИЯ", CYAN, True),
            ("", WHITE, False),
            ("Вы - вирус, стремящийся захватить организм.", WHITE, False),
            ("Ваша задача пройти от кровеносной системы до мозга.", WHITE, False),
            ("", WHITE, False),
            ("УПРАВЛЕНИЕ", CYAN, True),
            ("", WHITE, False),
            ("WASD или стрелки - перемещение", WHITE, False),
            ("SPACE - пропустить ход (+5 ATP)", WHITE, False),
            ("C - создать вирус-клон (затраты: 30 белка)", WHITE, False),
            ("E - активировать выход на уровне", WHITE, False),
            ("ESC - пауза", WHITE, False),
            ("", WHITE, False),
            ("РЕСУРСЫ", CYAN, True),
            ("", WHITE, False),
            ("ATP (энергия) тратится на движение и атаку.", GREEN, False),
            ("Белок нужен для создания клонов.", CYAN, False),
            ("РНК позволяет выбирать мутации.", PURPLE, False),
            ("", WHITE, False),
            ("ВРАГИ", CYAN, True),
            ("", WHITE, False),
            ("M - макрофаги: медленные, высокие показатели защиты.", PURPLE, False),
            ("N - нейтрофилы: быстрое перемещение, средние атаки.", ORANGE, False),
            ("B - B-клетки: дальняя атака.", BLUE, False),
            ("T - T-клетки: мощный ближний бой.", RED, False),
            ("D - дендритные клетки: призыв союзных войск.", YELLOW, False),
            ("* - тучная клетка: способна создавать токсичные зоны.", CYAN, False),
            ("", WHITE, False),
            ("УРОВНИ", CYAN, True),
            ("", WHITE, False),
            ("1-3: Кровеносная система - доминируют нейтрофилы.", WHITE, False),
            ("4-6: Лимфатическая система - преобладают лимфоциты.", WHITE, False),
            ("7-9: Лёгкие - распространены дендритные клетки.", WHITE, False),
            ("10-12: Печень - ограничение ресурсов.", WHITE, False),
            ("13: Мозг - финальное сражение.", WHITE, False),
            ("", WHITE, False),
            ("СОВЕТЫ", CYAN, True),
            ("", WHITE, False),
            ("- Используйте клонов для отвлечения врагов.", WHITE, False),
            ("- Избегайте попадания в токсичные зоны.", WHITE, False),
            ("- Получайте энергию (ATP) на кровеносных сосудах.", WHITE, False),
            ("- Применяйте выгодные мутации.", WHITE, False),
            ("- Уничтожьте всех врагов перед переходом на следующий уровень.", WHITE, False),
        ]
        arcade.draw_text("ГАЙД", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, YELLOW, font_size=64, anchor_x="center",
                         anchor_y="top", font_name=self.title_font)
        content_top = SCREEN_HEIGHT - 150
        content_bottom = 150
        visible_height = content_top - content_bottom
        rect_height = visible_height
        rect_x = 80
        rect_width = SCREEN_WIDTH - 160
        rect_y = content_bottom
        arcade.draw_lbwh_rectangle_filled(rect_x, rect_y, rect_width, rect_height, GRAY)
        text_start_y = content_top - 25
        line_height = 20
        for i, (text, color, is_header) in enumerate(guide_content):
            y = text_start_y - i * line_height + self.guide_scroll
            if y > content_top - 10 or y < rect_y + 15:
                continue
            if text:
                if is_header:
                    arcade.draw_text(text, rect_x + 15, y, color, font_size=18, font_name=self.font)
                else:
                    arcade.draw_text(text, rect_x + 15, y, color, font_size=14, font_name=self.small_font)
        # Индикатор прокрутки
        total_height = len(guide_content) * line_height
        if total_height > visible_height:
            max_scroll = total_height - visible_height
            current_scroll = min(self.guide_scroll, max_scroll)
            # Высота ползунка
            indicator_height = 20
            # Доступное пространство для перемещения ползунка
            track_height = rect_height - indicator_height
            scroll_ratio = current_scroll / max_scroll if max_scroll > 0 else 0
            indicator_y = rect_y + track_height - int(scroll_ratio * track_height)
            arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH - 80, indicator_y, 4, indicator_height, GREEN)
        # Подсказка о возвращении
        arcade.draw_text("ESC или ENTER - возврат | W/S - прокрутка",
                         SCREEN_WIDTH // 2, 80, GRAY, font_size=14,
                         anchor_x="center", anchor_y="bottom", font_name=self.small_font)



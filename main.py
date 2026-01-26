"""
L.A.T.E.N.D - Main entry point
Correct & verified for Arcade 3.3.3
"""

import arcade
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game import Game


class MenuView(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window)
        self.selected_item = 0
        self.menu_items = ["Начать игру", "Гайд", "Выход"]
        self.show_guide = False
        self.guide_scroll = 0

    # ================= DRAW =================

    def on_draw(self):
        self.clear()
        if self.show_guide:
            self.draw_guide()
        else:
            self.draw_menu()

    def draw_menu(self):
        # Background
        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            (15, 10, 15)
        )

        # Decorative circles
        for i in range(20):
            x = (i * 67) % SCREEN_WIDTH
            y = (i * 43) % SCREEN_HEIGHT
            arcade.draw_circle_outline(
                x, y,
                30 + i * 2,
                (25, 15, 25),
                1
            )

        # Title
        arcade.draw_text(
            "L.A.T.E.N.D",
            SCREEN_WIDTH // 2,
            150,
            arcade.color.GREEN,
            72,
            anchor_x="center",
            align="center"
        )

        arcade.draw_text(
            "Вирусная инвазия",
            SCREEN_WIDTH // 2,
            220,
            arcade.color.CYAN,
            32,
            anchor_x="center",
            align="center"
        )

        # Menu items
        for i, text in enumerate(self.menu_items):
            y = 350 + i * 60

            if i == self.selected_item:
                arcade.draw_lbwh_rectangle_filled(
                    SCREEN_WIDTH // 2 - 120,
                    y,
                    240,
                    45,
                    (30, 40, 30)
                )
                arcade.draw_lbwh_rectangle_outline(
                    SCREEN_WIDTH // 2 - 120,
                    y,
                    240,
                    45,
                    arcade.color.GREEN,
                    2
                )
                prefix = "> "
            else:
                prefix = "  "

            arcade.draw_text(
                prefix + text,
                SCREEN_WIDTH // 2,
                y + 8,
                arcade.color.WHITE if i == self.selected_item else arcade.color.GRAY,
                32,
                anchor_x="center",
                align="center"
            )

        arcade.draw_text(
            "W/S или ↑↓ — выбор | ENTER — подтвердить",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 50,
            arcade.color.GRAY,
            20,
            anchor_x="center",
            align="center"
        )

    def draw_guide(self):
        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            (15, 10, 15)
        )

        arcade.draw_text(
            "ГАЙД",
            SCREEN_WIDTH // 2,
            50,
            arcade.color.YELLOW,
            64,
            anchor_x="center",
            align="center"
        )

        y = 120 - self.guide_scroll
        guide = [
            ("КОНЦЕПЦИЯ", arcade.color.CYAN),
            "Вы — вирус внутри человеческого организма.",
            "",
            ("УПРАВЛЕНИЕ", arcade.color.CYAN),
            "W/A/S/D или стрелки — движение",
            "ESC — назад",
        ]

        for item in guide:
            if isinstance(item, tuple):
                arcade.draw_text(item[0], 100, y, item[1], 28)
            else:
                arcade.draw_text(item, 100, y, arcade.color.WHITE, 20)
            y += 30

        arcade.draw_text(
            "ESC или ENTER — назад | W/S — прокрутка",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 30,
            arcade.color.GRAY,
            18,
            anchor_x="center",
            align="center"
        )

    # ================= INPUT =================

    def on_key_press(self, key, modifiers):
        if not self.show_guide:
            if key in (arcade.key.W, arcade.key.UP):
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            elif key in (arcade.key.S, arcade.key.DOWN):
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            elif key in (arcade.key.ENTER, arcade.key.SPACE):
                if self.selected_item == 0:
                    view = GameView(self.window)
                    self.window.show_view(view)
                    view.init_new_game()
                elif self.selected_item == 1:
                    self.show_guide = True
                elif self.selected_item == 2:
                    self.window.close()
        else:
            if key in (arcade.key.ESCAPE, arcade.key.ENTER):
                self.show_guide = False
                self.guide_scroll = 0
            elif key in (arcade.key.W, arcade.key.UP):
                self.guide_scroll = max(0, self.guide_scroll - 30)
            elif key in (arcade.key.S, arcade.key.DOWN):
                self.guide_scroll += 30


class GameView(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window)
        self.game = Game(window)

    def on_draw(self):
        self.clear()
        self.game.on_draw()

    def on_update(self, delta_time: float):
        self.game.on_update(delta_time)

    def on_key_press(self, key, modifiers):
        return self.game.on_key_press(key, modifiers)

    def init_new_game(self):
        self.game.init_new_game()


class MainWindow(arcade.Window):
    def __init__(self):
        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            "L.A.T.E.N.D",
            update_rate=1 / FPS
        )
        arcade.set_background_color(arcade.color.BLACK)
        self.show_view(MenuView(self))


def main():
    MainWindow()
    arcade.run()


if __name__ == "__main__":
    main()


# app.py
import arcade
from game import Game
from menu import Menu
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

class Application(arcade.Window):
    # Главный класс приложения, управляющий переключением между меню и игрой
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "L.A.T.E.N.D")
        # Инициализация меню и игры
        self.menu = Menu(self)
        self.game = Game(self)
        # Текущее состояние приложения
        self.state = "menu"

    # Функция обновления логики игры
    def on_update(self, delta_time):
        if self.state == "game":
            self.game.update()

    # Функция отрисовки текущего состояния
    def on_draw(self):
        if self.state == "menu":
            self.menu.render_main_menu()
        elif self.state == "guide":
            self.menu.render_guide()
        elif self.state == "game":
            self.game.render()

    # Функция обработки нажатий клавиш
    def on_key_press(self, key, modifiers):
        # Обработка ввода в главном меню
        if self.state == "menu":
            action = self.menu.handle_input(key)
            if action == "start":
                self.state = "game"
                self.game.init_new_game()
            elif action == "guide":
                self.state = "guide"
            elif action == "quit":
                arcade.close_window()
        # Обработка ввода в руководстве
        elif self.state == "guide":
            if self.menu.handle_guide_input(key):
                self.state = "menu"
        # Обработка ввода в игре
        elif self.state == "game":
            result = self.game.handle_input(key)
            if result == "menu":
                self.state = "menu"

# Основная функция запуска приложения
def main():
    app = Application()
    arcade.run()

if __name__ == "__main__":
    main()
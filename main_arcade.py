import arcade


class LATENDGame(arcade.Window):
    def __init__(self):
        super().__init__(
            width=1280,
            height=720,
            title="L.A.T.E.N.D",
            update_rate=1 / 60
        )

        # Загружаем меню
        from views.menu_view_final import MenuViewFinal
        self.menu_view = MenuViewFinal()

        # Показываем меню
        self.show_view(self.menu_view)

        print("Игра запущена!")

    def start_new_game(self):
        try:
            from views.game_view import GameView
            self.game_view = GameView()
            self.show_view(self.game_view)
        except Exception as e:
            print(f"Ошибка: {e}")
            self.show_view(self.menu_view)

    def show_guide(self):
        try:
            from views.guide_view import GuideView
            self.guide_view = GuideView()
            self.show_view(self.guide_view)
        except:
            print("Гайд временно недоступен")
            self.show_view(self.menu_view)


def main():
    try:
        game = LATENDGame()
        arcade.run()
    except Exception as e:
        print(f"Ошибка: {e}")
        input("Нажмите Enter...")


if __name__ == "__main__":
    main()
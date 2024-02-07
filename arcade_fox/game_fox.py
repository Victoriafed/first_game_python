import arcade

SCREEN_TITLE = "Fox game"
DEFAULT_SCREEN_WIDTH = 800
DEFAULT_SCREEN_HEIGHT = 600
TILE_SCALING = 0.5
GRAVITY = 0.25
PLAYER_MOVEMENT_SPEED = 5
JUMP_SPEED = 10
CHARACTER_SCALING = 0.6
WIGHT_FOX = 100
HEIGHT_FOX = 50


class Fox(arcade.Sprite):
    """Player sprite"""

    def __init__(self):
        super().__init__()
        self.scale = CHARACTER_SCALING
        self.walk_images = []
        for i in range(2):
            self.walk_images.append(arcade.load_texture(f'images/fox{i}.png'))
        self.texture = self.walk_images[1]

    def update_animation(self, delta_time=1 / 60):
        if self.change_x < 0:
            self.texture = self.walk_images[0]
        elif self.change_x > 0:
            self.texture = self.walk_images[1]


class MyGame(arcade.View):
    def __init__(self):
        super().__init__()

        self.score = 0
        self.player_list = None
        self.wall_list = None
        self.player_sprite = None
        self.physics_engine = None
        self.tile_map = None
        self.camera_sprites = None
        self.camera_gui = None
        self.collect_apple_sound = arcade.load_sound(":resources:sounds/coin1.wav")

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.camera_sprites = arcade.Camera(DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT)
        self.camera_gui = arcade.Camera(DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT)

        self.player_sprite = Fox()
        self.player_sprite.center_x = 200
        self.player_sprite.center_y = 100
        self.player_list.append(self.player_sprite)

        map_name = "fox_level1.json"
        layer_options = {
            "Walls": {
                "use_spatial_hash": True,
            },
            "Apple": {
                "use_spatial_hash": True,
            },
        }
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.scene.add_sprite_list_after("Player", 'Walls')
        self.scene.add_sprite("Player", self.player_sprite)

        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.scene['Walls'],
            gravity_constant=GRAVITY
        )

    def on_draw(self):
        self.clear()
        self.camera_sprites.use()

        self.scene.draw()
        self.player_list.draw()

        self.camera_gui.use()

        score_text = f"Score: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.BLACK,
            18,
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            if key == arcade.key.UP:
                if self.physics_engine.can_jump():
                    self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.ESCAPE:
            self.window.close()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def center_camera_to_player(self, speed=0.2):
        screen_center_x = self.player_sprite.center_x - (self.camera_sprites.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
                self.camera_sprites.viewport_height / 2
        )
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera_sprites.move_to(player_centered, speed)

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.player_sprite.update_animation()
        self.center_camera_to_player()

        apple_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene['Apple']
        )
        for apple in apple_hit_list:
            arcade.play_sound(self.collect_apple_sound)
            apple.remove_from_sprite_lists()
            self.score += 1


class MenuView(arcade.View):
    bg_music = arcade.load_sound("bg_music.mp3")
    bg_music = arcade.play_sound(bg_music)
    bg_music.volume = 0.2

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(400, 300, 800,
                                      600, arcade.load_texture("images/background.png"))
        arcade.draw_text("Fox game", DEFAULT_SCREEN_WIDTH / 2, DEFAULT_SCREEN_HEIGHT - 200,
                         arcade.color.BLACK, font_size=50, anchor_x="center")
        arcade.draw_text("Click to Start", DEFAULT_SCREEN_WIDTH / 2, DEFAULT_SCREEN_HEIGHT / 2,
                         arcade.color.BLACK, font_size=20, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        game_view = MyGame()
        game_view.setup()
        self.window.show_view(game_view)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.close()
        if key == arcade.key.ENTER:
            game_view = MyGame()
            game_view.setup()
            self.window.show_view(game_view)


if __name__ == "__main__":
    window = arcade.Window(DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = MenuView()
    window.show_view(start_view)
    arcade.run()

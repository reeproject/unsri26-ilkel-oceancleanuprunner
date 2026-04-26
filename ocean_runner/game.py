from pathlib import Path

import pygame

from .assets import AssetLoader
from .audio import AudioManager
from .config import BASE_HEIGHT, BASE_WIDTH, FPS, LANES
from .gameplay import GameplayController
from .input import InputHandler
from .models import Entity
from .rendering import OceanRenderer
from .storage import StorageManager


class OceanRunner:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Ocean Cleanup Runner")

        info = pygame.display.Info()
        self.width = max(960, min(info.current_w - 80, 1600))
        self.height = max(540, min(info.current_h - 80, 900))
        self.scale_x = self.width / BASE_WIDTH
        self.scale_y = self.height / BASE_HEIGHT
        self.scale = min(self.scale_x, self.scale_y)

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", max(22, int(30 * self.scale)), bold=True)
        self.small_font = pygame.font.SysFont("arial", max(16, int(20 * self.scale)))
        self.medium_font = pygame.font.SysFont("arial", max(18, int(24 * self.scale)), bold=True)
        self.title_font = pygame.font.SysFont("arial", max(38, int(54 * self.scale)), bold=True)

        self.root_dir = Path(__file__).resolve().parent.parent
        self.assets_dir = self.root_dir / "assets"
        self.asset_loader = AssetLoader(self.assets_dir, self.sx, self.sy)
        self.sprites = self.asset_loader.load_sprites(self.width, self.height)
        self.storage = StorageManager(self.root_dir)
        self.settings = self.storage.load_settings()
        self.records = self.storage.load_records()
        self.audio = AudioManager(self.settings, self.assets_dir)
        self.audio.play_music()

        self.bg_scroll = 0.0
        self.lane_gap = self.height // (LANES + 1)
        self.player_x = self.sx(210)
        self.base_menu_items = ["PLAY", "GUIDE", "HIGH SCORE", "SETTINGS", "EXIT"]
        self.settings_items = ["SFX", "MUSIC", "RESET HIGH SCORE", "CREDIT", "BACK"]
        self.menu_index = 0
        self.settings_index = 0
        self.state = "menu"
        self.previous_state = "menu"
        self.menu_from_pause = False
        self.confirm_action: str | None = None
        self.confirm_message = ""
        self.pending_reset_confirm = False
        self.last_score = 0
        self.last_result_saved = False
        self.last_run_was_highscore = False
        self.resume_countdown = 0.0

        self.gameplay = GameplayController(self)
        self.renderer = OceanRenderer(self)
        self.input_handler = InputHandler(self)
        self.gameplay.reset()

    def sx(self, value: float) -> int:
        return int(value * self.scale_x)

    def sy(self, value: float) -> int:
        return int(value * self.scale_y)

    def ss(self, value: float) -> int:
        return max(1, int(value * self.scale))

    def lane_center(self, lane: int) -> int:
        return (lane + 1) * self.lane_gap

    def top_score(self) -> int:
        return max((int(record["score"]) for record in self.records), default=0)

    def current_menu_items(self) -> list[str]:
        items = list(self.base_menu_items)
        if self.menu_from_pause:
            items = [item for item in items if item != "HIGH SCORE"]
            items.insert(0, "RESUME")
        return items

    def save_settings(self) -> None:
        self.storage.save_settings(self.settings)
        self.audio.apply_settings(self.settings)

    def switch_state(self, state: str) -> None:
        self.previous_state = self.state
        self.state = state
        if state != "menu":
            self.menu_from_pause = False
        self.pending_reset_confirm = False

    def entity_rect(self, entity: Entity) -> pygame.Rect:
        y = self.lane_center(entity.lane)
        if entity.kind == "trash":
            return pygame.Rect(int(entity.x) - self.sx(14), y - self.sy(20), self.sx(28), self.sy(40))
        if entity.kind == "mine":
            return pygame.Rect(int(entity.x) - self.sx(18), y - self.sy(18), self.sx(36), self.sy(36))
        if entity.kind == "net":
            return pygame.Rect(int(entity.x) - self.sx(20), y - self.sy(22), self.sx(40), self.sy(44))
        return pygame.Rect(int(entity.x) - self.sx(20), y - self.sy(24), self.sx(40), self.sy(48))

    def player_rect(self) -> pygame.Rect:
        return pygame.Rect(self.player_x - self.sx(14), int(self.player_y) - self.sy(34), self.sx(28), self.sy(68))

    def shark_bite_rect(self) -> pygame.Rect:
        shark_x = self.shark_center_x()
        shark_y = int(self.shark_y)
        return pygame.Rect(shark_x + self.sx(18), shark_y - self.sy(14), self.sx(28), self.sy(28))

    def shark_center_x(self) -> int:
        player_back_x = self.player_x - self.sx(30)
        return int(player_back_x - max(0, self.shark_distance) - self.sx(88))

    def update(self, dt: float) -> None:
        self.gameplay.update(dt)

    def draw(self) -> None:
        self.renderer.draw()

    def handle_input(self, event: pygame.event.Event) -> None:
        self.input_handler.handle_input(event)

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_input(event)
            self.update(dt)
            self.draw()
        pygame.quit()

import random
from typing import TYPE_CHECKING

import pygame

from .config import FORWARD_SPEED_MAX, FORWARD_SPEED_START, LANES, SHARK_CATCH_DISTANCE, SHARK_DISTANCE_START, SPAWN_INTERVAL_MS
from .models import Bubble, Entity

if TYPE_CHECKING:
    from .game import OceanRunner


class GameplayController:
    def __init__(self, app: "OceanRunner") -> None:
        self.app = app

    def reset(self) -> None:
        self.app.player_lane = 1
        self.app.player_y = float(self.app.lane_center(self.app.player_lane))
        self.app.entities: list[Entity] = []
        self.app.bubbles = self.make_bubbles()
        self.app.spawn_timer = 0.0
        self.app.distance = 0.0
        self.app.speed = FORWARD_SPEED_START
        self.app.score = 0.0
        self.app.trash_collected = 0
        self.app.hit_flash = 0
        self.app.shark_distance = SHARK_DISTANCE_START
        self.app.shark_y = self.app.player_y
        self.app.safe_lane = 1
        self.app.last_pattern = "none"
        self.app.game_over = False
        self.app.last_result_saved = False

    def start_game(self) -> None:
        self.reset()
        self.app.switch_state("playing")
        self.app.resume_countdown = 0.0
        self.app.audio.play_sfx("confirm")

    def pause_game(self) -> None:
        if self.app.state == "playing":
            self.app.menu_from_pause = True
            self.app.switch_state("menu")
            self.app.audio.play_sfx("select")

    def resume_game_with_countdown(self) -> None:
        self.app.resume_countdown = 3.0
        self.app.menu_from_pause = False
        self.app.switch_state("countdown")
        self.app.audio.play_sfx("confirm")
        self.app.audio.play_sfx("countdown")

    def open_confirmation(self, action: str, message: str) -> None:
        self.app.confirm_action = action
        self.app.confirm_message = message
        self.app.audio.play_sfx("select")

    def close_confirmation(self) -> None:
        self.app.confirm_action = None
        self.app.confirm_message = ""

    def execute_confirmation(self) -> bool:
        action = self.app.confirm_action
        self.close_confirmation()
        if action == "restart_run":
            self.start_game()
        elif action == "reset_scores":
            self.app.storage.reset_records()
            self.app.records = []
            self.app.audio.play_sfx("confirm")
        elif action == "exit_game":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        else:
            return False
        return True

    def finish_run(self) -> None:
        if self.app.last_result_saved:
            return
        self.app.last_score = int(self.app.score)
        previous_best = self.app.top_score()
        self.app.storage.append_record(self.app.last_score)
        self.app.records = self.app.storage.load_records()
        self.app.last_run_was_highscore = self.app.last_score > previous_best
        self.app.last_result_saved = True
        self.app.audio.play_sfx("game_over")
        self.app.switch_state("game_over")

    def make_bubbles(self) -> list[Bubble]:
        bubbles: list[Bubble] = []
        for _ in range(22):
            bubbles.append(
                Bubble(
                    x=random.uniform(0, self.app.width),
                    y=random.uniform(self.app.sy(20), self.app.height - self.app.sy(20)),
                    radius=random.randint(self.app.ss(4), self.app.ss(10)),
                    speed=random.uniform(self.app.sx(18), self.app.sx(54)),
                    drift=random.uniform(self.app.sy(4), self.app.sy(16)),
                    phase=random.uniform(0, 6.28),
                )
            )
        return bubbles

    def _random_variant(self, sprite_key: str) -> int:
        variants = self.app.sprites.get(sprite_key, [])
        return random.randrange(len(variants)) if variants else 0

    def spawn_wave(self) -> None:
        lanes = [0, 1, 2]
        spawn_x = self.app.width + self.app.sx(90)
        prev_safe_lane = self.app.safe_lane
        candidate_safe_lanes = [prev_safe_lane]
        if prev_safe_lane > 0:
            candidate_safe_lanes.append(prev_safe_lane - 1)
        if prev_safe_lane < LANES - 1:
            candidate_safe_lanes.append(prev_safe_lane + 1)

        next_safe_lane = random.choice(candidate_safe_lanes)
        self.app.entities.append(Entity(next_safe_lane, spawn_x, "trash", self._random_variant("trash")))

        blocked_lanes = [lane for lane in lanes if lane != next_safe_lane]
        if next_safe_lane != prev_safe_lane:
            pattern = "transition"
            transition_block = next(lane for lane in blocked_lanes if lane != prev_safe_lane)
            kind = random.choice(["mine", "coral", "net"])
            variant = self._random_variant("net") if kind == "net" else self._random_variant("coral") if kind == "coral" else 0
            self.app.entities.append(Entity(transition_block, spawn_x + self.app.sx(80), kind, variant))
            if random.random() < 0.4:
                kind = random.choice(["mine", "coral"])
                variant = self._random_variant("coral") if kind == "coral" else 0
                self.app.entities.append(Entity(transition_block, spawn_x + self.app.sx(170), kind, variant))
        else:
            pattern = random.choice(["none", "single", "double", "offset"])
            if pattern == "single":
                lane = random.choice(blocked_lanes)
                kind = random.choice(["mine", "coral", "net"])
                variant = self._random_variant("net") if kind == "net" else self._random_variant("coral") if kind == "coral" else 0
                self.app.entities.append(Entity(lane, spawn_x + self.app.sx(90), kind, variant))
            elif pattern == "double":
                for lane in blocked_lanes:
                    kind = random.choice(["mine", "coral"])
                    variant = self._random_variant("coral") if kind == "coral" else 0
                    self.app.entities.append(Entity(lane, spawn_x + self.app.sx(110), kind, variant))
            elif pattern == "offset":
                first_kind = random.choice(["mine", "net"])
                first_variant = self._random_variant("net") if first_kind == "net" else 0
                self.app.entities.append(Entity(blocked_lanes[0], spawn_x + self.app.sx(80), first_kind, first_variant))
                self.app.entities.append(Entity(blocked_lanes[1], spawn_x + self.app.sx(180), "coral", self._random_variant("coral")))

        self.app.safe_lane = next_safe_lane
        self.app.last_pattern = pattern

    def _update_bubbles(self, dt: float) -> None:
        for bubble in self.app.bubbles:
            bubble.x -= dt * bubble.speed
            bubble.y += dt * bubble.drift * pygame.math.Vector2(1, 0).rotate_rad(pygame.time.get_ticks() * 0.0012 + bubble.phase).x
            if bubble.x < -self.app.sx(30):
                bubble.x = self.app.width + random.randint(0, self.app.sx(120))
                bubble.y = random.uniform(self.app.sy(20), self.app.height - self.app.sy(20))

    def _update_gameplay(self, dt: float) -> None:
        self.app.distance += dt * self.app.speed
        self.app.speed = min(FORWARD_SPEED_START + self.app.distance * 0.018, FORWARD_SPEED_MAX)
        self.app.spawn_timer += dt * 1000
        self.app.bg_scroll = (self.app.bg_scroll + dt * (self.app.speed * 0.35)) % max(1, self.app.width)

        required_spawn_gap = SPAWN_INTERVAL_MS
        if self.app.last_pattern in {"double", "transition", "offset"}:
            required_spawn_gap += 260
        if self.app.spawn_timer >= required_spawn_gap:
            self.spawn_wave()
            self.app.spawn_timer = 0

        self.app.player_y += (self.app.lane_center(self.app.player_lane) - self.app.player_y) * min(1, dt * 14)
        self.app.shark_y += (self.app.player_y - self.app.shark_y) * min(1, dt * 7)
        self._update_bubbles(dt)

        for entity in self.app.entities:
            entity.x -= dt * self.app.speed

        player_rect = self.app.player_rect()
        survivors: list[Entity] = []
        for entity in self.app.entities:
            if entity.x < -self.app.sx(100):
                continue
            if player_rect.colliderect(self.app.entity_rect(entity)):
                if entity.kind == "trash":
                    self.app.trash_collected += 1
                    self.app.score += 10
                    self.app.shark_distance = min(SHARK_DISTANCE_START, self.app.shark_distance + 22)
                    self.app.audio.play_sfx("pickup")
                    continue
                self.app.score = max(0, self.app.score - 8)
                self.app.shark_distance -= 70 if entity.kind == "mine" else 55
                self.app.hit_flash = 10
                self.app.audio.play_sfx("hit")
                continue
            survivors.append(entity)

        self.app.entities = survivors
        self.app.score += dt * 2.4
        self.app.shark_distance -= dt * (14 + (self.app.speed - FORWARD_SPEED_START) * 0.02)
        if self.app.hit_flash > 0:
            self.app.hit_flash -= 1
        if self.app.shark_distance <= SHARK_CATCH_DISTANCE or self.app.shark_bite_rect().colliderect(player_rect):
            self.app.shark_distance = float(SHARK_CATCH_DISTANCE)
            self.app.game_over = True
            self.finish_run()

    def _update_countdown(self, dt: float) -> None:
        previous_count = max(1, int(self.app.resume_countdown) + (0 if self.app.resume_countdown.is_integer() else 1))
        self.app.resume_countdown = max(0.0, self.app.resume_countdown - dt)
        next_count = max(0, int(self.app.resume_countdown) + (0 if self.app.resume_countdown.is_integer() else 1))
        if 0 < next_count < previous_count:
            self.app.audio.play_sfx("countdown")
        if self.app.resume_countdown <= 0:
            self.app.switch_state("playing")

    def _update_background_only(self, dt: float) -> None:
        self.app.bg_scroll = (self.app.bg_scroll + dt * 26) % max(1, self.app.width)
        for bubble in self.app.bubbles:
            bubble.x -= dt * bubble.speed * 0.35
            if bubble.x < -self.app.sx(30):
                bubble.x = self.app.width + random.randint(0, self.app.sx(120))

    def update(self, dt: float) -> None:
        if self.app.state == "playing":
            self._update_gameplay(dt)
        elif self.app.state == "countdown":
            self._update_countdown(dt)
        elif self.app.state == "menu" and self.app.menu_from_pause:
            return
        else:
            self._update_background_only(dt)

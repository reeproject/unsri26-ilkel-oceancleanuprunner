import math
from array import array
from pathlib import Path

import pygame


class AudioManager:
    def __init__(self, settings: dict[str, bool], assets_dir: Path) -> None:
        self.available = False
        self.settings = settings
        self.assets_dir = assets_dir
        self.sfx_dir = self.assets_dir / "sfx"
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.music_sound: pygame.mixer.Sound | None = None
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
        except pygame.error:
            return
        self.available = True
        custom_sounds = self._load_custom_sounds()
        self.sounds = {
            "pickup": custom_sounds.get("pickup") or self._make_tone_sequence([(660, 0.05), (880, 0.08)], 0.22),
            "hit": custom_sounds.get("hit") or self._make_tone_sequence([(210, 0.08), (140, 0.12)], 0.28),
            "select": custom_sounds.get("select") or self._make_tone_sequence([(520, 0.05)], 0.18),
            "confirm": custom_sounds.get("confirm") or self._make_tone_sequence([(420, 0.05), (620, 0.08)], 0.18),
            "countdown": custom_sounds.get("countdown") or self._make_tone_sequence([(520, 0.08)], 0.18),
            "game_over": self._make_tone_sequence([(260, 0.12), (180, 0.18), (120, 0.24)], 0.24),
        }
        self.music_sound = self._make_tone_sequence(
            [(196, 0.25), (220, 0.25), (247, 0.25), (220, 0.25), (174, 0.25), (196, 0.25), (220, 0.25), (196, 0.25)],
            0.08,
        )

    def _load_custom_sounds(self) -> dict[str, pygame.mixer.Sound]:
        custom: dict[str, pygame.mixer.Sound] = {}
        for name in ["pickup", "hit", "select", "confirm", "countdown"]:
            path = self.sfx_dir / f"{name}.mp3"
            if not path.exists():
                continue
            try:
                custom[name] = pygame.mixer.Sound(str(path))
            except pygame.error:
                continue
        return custom

    def _make_tone_sequence(self, notes: list[tuple[int, float]], volume: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        samples = array("h")
        attack = 0.08
        release = 0.12
        for frequency, duration in notes:
            frame_count = max(1, int(sample_rate * duration))
            for i in range(frame_count):
                progress = i / frame_count
                envelope = 1.0
                if progress < attack:
                    envelope = progress / attack
                elif progress > 1 - release:
                    envelope = max(0.0, (1 - progress) / release)
                value = math.sin(2 * math.pi * frequency * (i / sample_rate))
                samples.append(int(32767 * volume * envelope * value))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def apply_settings(self, settings: dict[str, bool]) -> None:
        self.settings = settings
        if not self.available:
            return
        if self.settings.get("music_enabled", True):
            self.play_music()
        else:
            pygame.mixer.stop()

    def play_music(self) -> None:
        if not self.available or not self.settings.get("music_enabled", True) or self.music_sound is None:
            return
        if pygame.mixer.get_busy():
            return
        self.music_sound.play(loops=-1)

    def play_sfx(self, name: str) -> None:
        if not self.available or not self.settings.get("sfx_enabled", True):
            return
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

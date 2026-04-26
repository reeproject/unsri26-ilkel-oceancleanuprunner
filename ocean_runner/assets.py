from pathlib import Path

import pygame


class AssetLoader:
    def __init__(self, assets_dir: Path, sx, sy) -> None:
        self.assets_dir = assets_dir
        self.sprites_dir = self.assets_dir / "sprites"
        self.sx = sx
        self.sy = sy

    def load_image(self, filename: str, size: tuple[int, int], remove_white: bool = False) -> pygame.Surface | None:
        path = self.sprites_dir / filename
        if not path.exists():
            path = self.assets_dir / filename
        if not path.exists():
            return None

        try:
            image = pygame.image.load(str(path))
        except pygame.error:
            return None

        has_alpha = image.get_alpha() is not None
        image = image.convert_alpha() if has_alpha else image.convert()
        image = pygame.transform.smoothscale(image, size)

        if remove_white or not has_alpha:
            image.set_colorkey((255, 255, 255))

        return image

    def load_first_available(self, filenames: list[str], size: tuple[int, int], remove_white: bool = False) -> pygame.Surface | None:
        for filename in filenames:
            image = self.load_image(filename, size, remove_white=remove_white)
            if image is not None:
                return image
        return None

    def load_sprites(self, width: int, height: int) -> dict[str, pygame.Surface | list[pygame.Surface]]:
        trash_size = (self.sx(65), self.sy(65))
        net_size = (self.sx(85), self.sy(70))
        return {
            "background": self.load_first_available(["bg.jpeg", "bg.png", "bg.jpg", "bg.webp"], (width, height)),
            "player": self.load_first_available(["diver.png", "diver.webp", "diver.jpg"], (self.sx(132), self.sy(74))),
            "shark": self.load_first_available(["shark.png", "shark.webp", "shark.jpg"], (self.sx(210), self.sy(126))),
            "coral": [
                sprite
                for sprite in [
                    self.load_first_available(["coral1.png", "coral1.webp", "coral1.jpg", "coral1.jpeg"], (self.sx(82), self.sy(82)), remove_white=True),
                    self.load_first_available(["coral2.png", "coral2.webp", "coral2.jpg", "coral2.jpeg"], (self.sx(82), self.sy(82)), remove_white=True),
                    self.load_first_available(["coral3.png", "coral3.webp", "coral3.jpg", "coral3.jpeg"], (self.sx(82), self.sy(82)), remove_white=True),
                    self.load_first_available(["coral4.png", "coral4.webp", "coral4.jpg", "coral4.jpeg"], (self.sx(82), self.sy(82)), remove_white=True),
                    self.load_first_available(["coral.png", "coral.webp", "coral.jpg", "coral.jpeg"], (self.sx(82), self.sy(82)), remove_white=True),
                ]
                if sprite is not None
            ],
            "trash": [
                sprite
                for sprite in [
                    self.load_first_available(["bottle.png", "bottle.webp", "bottle.jpg"], trash_size, remove_white=True),
                    self.load_first_available(["plastic.png", "plastic.webp", "plastic.jpg"], trash_size, remove_white=True),
                ]
                if sprite is not None
            ],
            "net": [
                sprite
                for sprite in [
                    self.load_first_available(["fishing-net.png", "fishing-net.webp", "fishing-net.jpg"], net_size),
                    self.load_first_available(["net1.png", "net1.webp", "net1.jpg"], net_size),
                    self.load_first_available(["net2.png", "net2.webp", "net2.jpg"], net_size),
                    self.load_first_available(["net3.png", "net3.webp", "net3.jpg"], net_size),
                ]
                if sprite is not None
            ],
        }

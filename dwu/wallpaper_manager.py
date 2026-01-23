from __future__ import annotations

import os
import httpx
import click

from dwu.scraper import WallpaperScraper
from dwu.metadata import WallpaperMetadata
from dwu.skip_manager import SkipManager
from dwu.wallresult import WallResult
from dwu.backends import get_backend, WallpaperBackend
from dwu.utils import get_cache_dir, infer_extension, detect_display_server, get_display_resolution

from PIL import Image, ImageDraw, ImageFont

class WallpaperSetError(Exception):
    pass

class ImageDownloadError(Exception):
    pass
    
class WallpaperManager:
    def __init__(self, root_url: str = 'https://wallpaper-a-day.com', resolution: str | None = None) -> None:
        self._scraper = WallpaperScraper(root_url=root_url, resolution=resolution)
        self._client = httpx.Client(timeout=30.0)
        self._cache_dir = get_cache_dir()
        self._metadata_path = os.path.join(self._cache_dir, "current_wallpaper.json")
        self._backend: WallpaperBackend | None = get_backend(detect_display_server())
        
    def update_back(self, days: int) -> WallResult:
        meta = self._scraper.get_metadata(days)
        return self._apply_wallpaper(meta)
        
    def update_auto(self) -> WallResult:
        walls = self._scraper.get_all()
        skips = SkipManager()
        
        for i, meta in enumerate(walls):
            if skips.is_skipped(meta.img_url):
                continue
        
            result = self._apply_wallpaper(meta)
            if result == WallResult.ALREADY_SET:
                return result
            return WallResult.TODAY if i == 0 else WallResult.MOST_RECENT
        
        return WallResult.NO_VALID
    
    def _apply_wallpaper(self, meta: WallpaperMetadata) -> WallResult:
        old_meta = WallpaperMetadata.load()
        
        # Get the previous wallpaper path for cleanup before metadata is overwritten
        previous_wallpaper_path = None
        if old_meta and old_meta.img_url != meta.img_url:
            previous_wallpaper_path = self._get_image_path(old_meta)
        
        if old_meta and old_meta.img_url == meta.img_url:
            if old_meta.successfully_set:
                if self._backend:
                    if self.currently_set(meta):
                        return WallResult.ALREADY_SET
            
            # reapply
            image_path = self._get_image_path(meta)
            if os.path.exists(image_path):
                self._set_wallpaper(image_path, meta, previous_wallpaper_path)
                return WallResult.SET
        
        meta.save()
        filename = self.download_image(meta)
        if meta.add_watermark:
            self._watermark_image(filename, meta)
        self._set_wallpaper(filename, meta, previous_wallpaper_path)
        
        return WallResult.SET
    
    def get_backend_name(self) -> str:
        return self._backend.name if self._backend is not None else "None"
    
    def currently_set(self, meta):
        expected = os.path.abspath(self._get_image_path(meta))
        current = self._backend.get_current_wallpaper() if self._backend is not None else None
        
        if current is None:
            return True

        if os.path.abspath(current) == expected:
            return True
            
        return False
        
    def _watermark_image(self, img_path: str, metadata: WallpaperMetadata) -> None:
        img = Image.open(img_path)
        w, h = img.size
        dw, dh = get_display_resolution()
        
        target_ratio = dw/dh
        difx, dify = 0, 0
        if (w / h) > target_ratio: # image is too wide
            nw = int(target_ratio * h)
            difx = (nw - w)//2
        else: # image is too tall
            nh = int(w / target_ratio)
            dify = (nh - h)//2
            
            
        font_size = int(min(w, h) * 0.02)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc", font_size, index=0)
        except Exception as e:
            click.echo(e)
            try:
                font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", font_size)
            except Exception as ee:
                font = ImageFont.load_default()
                click.echo(ee)
        
        draw = ImageDraw.Draw(img)
        
        text = f"{metadata.artist}" if metadata.artist else ""
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        padding = int(min(w, h) * 0.015) 
        
        x = w - text_width - padding + difx
        y = h - text_height - padding + dify
        
        draw.text(
            (x, y),
            text,
            fill="white",
            font=font,
            stroke_width=1,
            stroke_fill="black",
        )
        
        img.save(img_path)
        
    def unwatermark(self, metadata: WallpaperMetadata) -> None:
        metadata.add_watermark = False
        metadata.save()
        filename = self.download_image(metadata)
        self._set_wallpaper(filename, metadata)
        
    def _get_image_path(self, metadata: WallpaperMetadata) -> str:
        ext = infer_extension(metadata.img_url)
        # Use unique filename based on day number so KDE detects it as a new file
        return os.path.join(self._cache_dir, f"wallpaper_day_{metadata.day}.{ext}")

    def download_image(self, metadata: WallpaperMetadata, sp: str | None = None) -> str:
        ext = infer_extension(metadata.img_url)
        # Use unique filename based on day number so KDE detects it as a new file
        save_path = sp or os.path.join(self._cache_dir, f"wallpaper_day_{metadata.day}.{ext}")
        
        response = self._client.get(metadata.img_url)
        if response.status_code != 200:
            raise ImageDownloadError(f"Failed to download image ({response.status_code})")
            
        with open(save_path, "wb") as f:
            f.write(response.content)
        
        return save_path
        
    def _set_wallpaper(self, filename: str, meta: WallpaperMetadata, previous_wallpaper_path: str | None = None) -> None:
        if not os.path.isfile(filename):
            raise WallpaperSetError("Wallpaper file not found")
        if not self._backend:
            raise WallpaperSetError("No wallpaper backend found")
        
        # Only delete if it's a different file (not the one we're about to set)
        if previous_wallpaper_path == filename:
            previous_wallpaper_path = None
            
        try:
            self._backend.set_wallpaper(os.path.abspath(filename))
        except Exception as e:
            raise WallpaperSetError(
                f"Failed to set wallpaper using {self._backend.name}: {e}"
            ) from e
        
        meta.successfully_set = True
        meta.save()
        
        # Clean up the previous wallpaper file after successfully setting the new one
        if previous_wallpaper_path and os.path.exists(previous_wallpaper_path):
            try:
                os.remove(previous_wallpaper_path)
            except OSError:
                # Ignore errors when deleting old files (e.g., permission issues)
                pass

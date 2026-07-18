"""Controlled visual inputs for the graduate-resume layout pipeline."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from graduate_resume_cli import CliError


FONT_MANIFEST_INVALID = "FONT_MANIFEST_INVALID"
PHOTO_ASSET_INVALID = "PHOTO_ASSET_INVALID"
THEME_INVALID = "THEME_INVALID"
_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


@dataclass(frozen=True, slots=True)
class PhotoFitPolicy:
    photo_fit: str = "contain"
    crop_policy: str = "forbid"
    preserve_aspect_ratio: bool = True
    allow_stretch: bool = False
    allow_controlled_crop: bool = False
    subject_safe_area_contract: str | None = None


@dataclass(frozen=True, slots=True)
class PhotoSlot:
    width_mm: float
    height_mm: float
    position: str


@dataclass(frozen=True, slots=True)
class ThemeSpec:
    key: str
    label: str
    layout: str
    photo_slot: PhotoSlot
    no_photo_behavior: str
    safe_margins_mm: tuple[int, int, int, int]
    column_ratio: tuple[int, int]
    palette: tuple[str, str, str]
    typography_pt: tuple[float, float, float, float]
    spacing_tokens: tuple[str, ...]
    photo_policy: PhotoFitPolicy = PhotoFitPolicy()


@dataclass(frozen=True, slots=True)
class PhotoAsset:
    """A logical relative asset identity; it intentionally excludes absolute paths and bytes."""

    logical_path: str
    mode: str = "photo"


@dataclass(frozen=True, slots=True)
class FrozenResumePlan:
    theme_key: str
    theme_label: str
    page_preference: str
    photo_mode: str
    photo: PhotoAsset | None
    photo_fit: str
    crop_policy: str
    preserve_aspect_ratio: bool
    allow_stretch: bool
    allow_controlled_crop: bool
    photo_slot: PhotoSlot | None
    no_photo_behavior: str
    font_manifest_hash: str

    def to_projection(self) -> dict[str, Any]:
        """Return a renderer input projection without the source image path or facts."""
        return {
            "theme": {"key": self.theme_key, "label": self.theme_label},
            "page_preference": self.page_preference,
            "photo_mode": self.photo_mode,
            "has_photo": self.photo is not None,
            "photo_policy": {
                "photo_fit": self.photo_fit,
                "crop_policy": self.crop_policy,
                "preserve_aspect_ratio": self.preserve_aspect_ratio,
                "allow_stretch": self.allow_stretch,
                "allow_controlled_crop": self.allow_controlled_crop,
            },
            "photo_slot": None if self.photo_slot is None else {
                "width_mm": self.photo_slot.width_mm,
                "height_mm": self.photo_slot.height_mm,
                "position": self.photo_slot.position,
            },
            "no_photo_behavior": self.no_photo_behavior,
            "font_manifest_hash": self.font_manifest_hash,
        }


_COMMON = {
    "safe_margins_mm": (14, 14, 15, 15),
    "typography_pt": (9, 10.5, 14, 22),
    "spacing_tokens": ("xs", "sm", "md", "lg", "xl"),
    "photo_policy": PhotoFitPolicy(),
}
THEME_SPECS: dict[str, ThemeSpec] = {
    "conservative": ThemeSpec("conservative", "保守稳妥", "single-column-right-photo", PhotoSlot(32, 42, "top-right"), "remove-slot-and-decoration", (14, 14, 15, 15), (100, 0), ("#FFFFFF", "#F2F4F7", "#1F4E79"), (9, 10.5, 14, 22), ("xs", "sm", "md", "lg", "xl")),
    "modern": ThemeSpec("modern", "现代简洁", "sidebar-photo", PhotoSlot(28, 36, "left-sidebar"), "move-sidebar-content-up", (14, 14, 15, 15), (31, 69), ("#FFFFFF", "#EFF5F4", "#0F766E"), (9, 10.5, 14, 22), ("xs", "sm", "md", "lg", "xl")),
    "expressive": ThemeSpec("expressive", "个性设计", "header-photo", PhotoSlot(30, 40, "header-right"), "expand-identity-bar", (14, 14, 15, 15), (38, 62), ("#FFFEFA", "#F3F1EA", "#8A6A20"), (9, 10.5, 14, 22), ("xs", "sm", "md", "lg", "xl")),
}
_ALIASES = {spec.label: key for key, spec in THEME_SPECS.items()}


def resolve_theme(value: str | None) -> ThemeSpec:
    key = (value or "conservative").strip()
    key = _ALIASES.get(key, key)
    try:
        return THEME_SPECS[key]
    except KeyError as exc:
        raise CliError(THEME_INVALID, "主题必须是 conservative、modern 或 expressive。") from exc


def _manifest_error() -> CliError:
    return CliError(FONT_MANIFEST_INVALID, "受控字体清单无效。")


def _validate_font_visibility(fonts_root: Path, entries: list[dict[str, Any]]) -> None:
    typst = shutil.which("typst")
    if typst is None:
        raise _manifest_error()
    completed = subprocess.run(
        [typst, "fonts", "--font-path", str(fonts_root), "--ignore-system-fonts", "--variants"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    output = completed.stdout
    if completed.returncode != 0 or "Noto Sans Mono CJK SC" not in output:
        raise _manifest_error()
    # The approved upstream Bold file exposes physical OpenType weight 700; the UI's
    # locked semantic 600 role selects this static Bold face rather than altering it.
    expected = {400: "Weight: 400", 600: "Weight: 700"}
    for entry in entries:
        if entry["path"] not in output or expected[entry["weight"]] not in output:
            raise _manifest_error()


def validate_font_manifest(fonts_root: Path) -> str:
    """Verify only the two approved skill-local fonts before planning begins."""
    try:
        manifest_path = fonts_root / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        source = manifest["source"]
        entries = manifest["fonts"]
        if set(manifest) != {"family", "source", "fonts"} or manifest["family"] != "Noto Sans Mono CJK SC":
            raise ValueError("manifest")
        if set(source) != {"kind", "upstream", "license", "license_file", "license_sha256"}:
            raise ValueError("source")
        if source["license"] != "SIL Open Font License 1.1" or source["license_file"] != "LICENSE.txt":
            raise ValueError("license")
        license_path = fonts_root / source["license_file"]
        if not license_path.is_file() or hashlib.sha256(license_path.read_bytes()).hexdigest() != source["license_sha256"]:
            raise ValueError("license hash")
        if not isinstance(entries, list) or len(entries) != 2 or {entry["weight"] for entry in entries} != {400, 600}:
            raise ValueError("weights")
        digest = hashlib.sha256()
        for entry in sorted(entries, key=lambda item: item["weight"]):
            if set(entry) != {"path", "family", "weight", "bytes", "sha256"} or entry["family"] != manifest["family"]:
                raise ValueError("entry")
            relative = PurePosixPath(entry["path"])
            if relative.is_absolute() or len(relative.parts) != 1 or relative.suffix != ".otf":
                raise ValueError("path")
            path = fonts_root / relative
            if not path.is_file() or path.stat().st_size != entry["bytes"]:
                raise ValueError("file")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != entry["sha256"]:
                raise ValueError("hash")
            digest.update(actual.encode("ascii"))
        _validate_font_visibility(fonts_root, entries)
        return digest.hexdigest()
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        raise _manifest_error() from exc


def _photo_error() -> CliError:
    return CliError(PHOTO_ASSET_INVALID, "照片资源无效。")


def _safe_relative_photo_path(raw: object) -> PurePosixPath:
    if not isinstance(raw, str) or not raw or "\\" in raw or ":" in raw or raw.startswith(("//", "http://", "https://")):
        raise _photo_error()
    raw_parts = raw.split("/")
    pure = PurePosixPath(raw)
    if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in raw_parts):
        raise _photo_error()
    return pure


def _is_image(path: Path) -> bool:
    try:
        payload = path.read_bytes()[:16]
    except OSError:
        return False
    return (path.suffix.lower() in {".jpg", ".jpeg"} and payload.startswith(b"\xff\xd8")) or (path.suffix.lower() == ".png" and payload.startswith(b"\x89PNG\r\n\x1a\n"))


def resolve_layout_photo(input_path: Path, assets_root: Path, photo: dict[str, Any], preferences: dict[str, Any]) -> PhotoAsset | None:
    """Resolve a verified local photo without returning physical path, bytes, or metadata."""
    photo_mode = preferences.get("photo_mode", "auto")
    if photo_mode == "no-photo" or photo.get("status") == "no-photo":
        return None
    raw = photo.get("path")
    if not isinstance(raw, str) or not raw:
        if photo_mode == "photo":
            raise _photo_error()
        return None
    pure = _safe_relative_photo_path(raw)
    try:
        root = assets_root.expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError("root")
        candidate = root
        for part in pure.parts:
            candidate = candidate / part
            mode = candidate.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise ValueError("symlink")
        info = candidate.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o444 == 0 or not _is_image(candidate):
            raise ValueError("unsafe")
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise _photo_error() from exc
    return PhotoAsset(logical_path=pure.as_posix())


def build_frozen_plan(theme: ThemeSpec, photo_mode: str, photo: PhotoAsset | None, font_manifest_hash: str, page_preference: str) -> FrozenResumePlan:
    policy = theme.photo_policy
    if policy.crop_policy == "controlled" and not (policy.allow_controlled_crop and policy.subject_safe_area_contract):
        raise CliError(THEME_INVALID, "受控裁切主题缺少主体安全区域契约。")
    if policy.crop_policy != "controlled" and policy.allow_controlled_crop:
        raise CliError(THEME_INVALID, "主题不得隐式启用裁切。")
    return FrozenResumePlan(
        theme_key=theme.key,
        theme_label=theme.label,
        page_preference=page_preference,
        photo_mode="photo" if photo else "no-photo",
        photo=photo,
        photo_fit=policy.photo_fit,
        crop_policy=policy.crop_policy,
        preserve_aspect_ratio=policy.preserve_aspect_ratio,
        allow_stretch=policy.allow_stretch,
        allow_controlled_crop=policy.allow_controlled_crop,
        photo_slot=theme.photo_slot if photo else None,
        no_photo_behavior=theme.no_photo_behavior,
        font_manifest_hash=font_manifest_hash,
    )

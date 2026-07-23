"""Deterministic, renderer-neutral application font assets."""

from dataclasses import dataclass
from enum import Enum
import hashlib
from pathlib import Path


INTER_FAMILY = "Inter"
INTER_VERSION = "4.1"
INTER_ASSET_DIR = Path(__file__).resolve().parent / "assets" / "fonts" / "inter"


class FontWeight(str, Enum):
    REGULAR = "regular"
    SEMIBOLD = "semibold"


class FontAssetError(ValueError):
    """Raised when an approved application font asset cannot be used safely."""


@dataclass(frozen=True)
class FontAsset:
    family: str
    version: str
    weight: FontWeight
    filename: str
    sha256: str


@dataclass(frozen=True)
class ValidatedFontAsset:
    definition: FontAsset
    path: Path


INTER_FONT_ASSETS = (
    FontAsset(
        family=INTER_FAMILY,
        version=INTER_VERSION,
        weight=FontWeight.REGULAR,
        filename="Inter-Regular.ttf",
        sha256="40d692fce188e4471e2b3cba937be967878f631ad3ebbbdcd587687c7ebe0c82",
    ),
    FontAsset(
        family=INTER_FAMILY,
        version=INTER_VERSION,
        weight=FontWeight.SEMIBOLD,
        filename="Inter-SemiBold.ttf",
        sha256="78a843fade9d4612a5567302fb595b56976eb5fcebf4fea5a5912d638bafcde3",
    ),
)


def font_asset_for_weight(weight):
    """Return one approved Inter asset without accepting arbitrary font paths."""
    try:
        requested_weight = weight if isinstance(weight, FontWeight) else FontWeight(weight)
    except (TypeError, ValueError) as error:
        raise FontAssetError("Unsupported Inter font weight.") from error

    for asset in INTER_FONT_ASSETS:
        if asset.weight == requested_weight:
            return asset
    raise FontAssetError("Unsupported Inter font weight.")


def validate_font_asset(asset, asset_dir=None):
    """Validate one asset using bounded errors that never expose absolute paths."""
    _validate_definition(asset)
    directory = Path(asset_dir) if asset_dir is not None else INTER_ASSET_DIR
    path = directory / asset.filename
    if not path.is_file():
        raise FontAssetError(f"Required font asset is missing: {asset.filename}")

    try:
        digest = _sha256(path)
    except OSError as error:
        raise FontAssetError(f"Required font asset cannot be read: {asset.filename}") from error
    if digest != asset.sha256:
        raise FontAssetError(f"Required font asset failed checksum validation: {asset.filename}")

    return ValidatedFontAsset(definition=asset, path=path)


def validate_inter_font_assets(asset_dir=None, assets=None):
    """Validate the complete approved Inter asset set."""
    definitions = tuple(assets) if assets is not None else INTER_FONT_ASSETS
    return tuple(validate_font_asset(asset, asset_dir=asset_dir) for asset in definitions)


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_definition(asset):
    if (
        not isinstance(asset, FontAsset)
        or Path(asset.filename).name != asset.filename
        or not asset.filename.endswith(".ttf")
        or len(asset.sha256) != 64
        or any(character not in "0123456789abcdef" for character in asset.sha256)
    ):
        raise FontAssetError("Font asset definition is invalid.")

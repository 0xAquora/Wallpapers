import os
import urllib.parse
from pathlib import Path

# Configuration
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"}
IGNORE_DIRS = {".git", ".github"}
COLUMNS = 3
README_FILE = "README.md"

HEADER = """# Wallpapers

A curated collection of desktop and mobile wallpapers.

---
"""


def get_images_by_folder(root: Path) -> dict[str, list[Path]]:
    grouped: dict[str, list[Path]] = {}

    for current_root, dirs, files in os.walk(root):
        # Skip hidden/ignored directories in-place
        dirs[:] = sorted(d for d in dirs if d not in IGNORE_DIRS and not d.startswith("."))

        rel_dir = Path(current_root).relative_to(root)
        folder_name = "Root" if str(rel_dir) == "." else rel_dir.as_posix()

        images = [
            rel_dir / f
            for f in sorted(files, key=str.lower)
            if Path(f).suffix.lower() in IMAGE_EXTENSIONS
        ]

        if images:
            grouped[folder_name] = images

    return grouped


def build_table(images: list[Path], folder_name: str) -> str:
    lines = []
    # Markdown table header
    lines.append("| " + " | ".join(["Preview"] * COLUMNS) + " |")
    lines.append("| " + " | ".join([":---:"] * COLUMNS) + " |")

    for i in range(0, len(images), COLUMNS):
        chunk = images[i : i + COLUMNS]
        cells = []

        for img_path in chunk:
            # URL-encode each path segment so spaces/symbols render on GitHub
            encoded_path = "/".join(
                urllib.parse.quote(part) for part in img_path.parts
            )
            name = img_path.name
            cell = (
                f'<a href="{encoded_path}">'
                f'<img src="{encoded_path}" alt="{name}" width="320" />'
                f"</a><br/>"
                f"<code>{name}</code><br/>"
                f"<sub>📁 {folder_name}</sub>"
            )
            cells.append(cell)

        # Pad incomplete final row
        while len(cells) < COLUMNS:
            cells.append("")

        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


def main() -> None:
    root = Path(".")
    grouped_images = get_images_by_folder(root)

    sections = [HEADER.strip()]

    # Quick table of contents if multiple folders exist
    if len(grouped_images) > 1:
        toc = ["## Folders"]
        for folder in grouped_images:
            anchor = folder.lower().replace(" ", "-").replace("/", "")
            toc.append(f"- [{folder}](#{anchor}) ({len(grouped_images[folder])})")
        sections.append("\n".join(toc))

    for folder, images in grouped_images.items():
        sections.append(f"## {folder}\n\n{build_table(images, folder)}")

    Path(README_FILE).write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    print(f"Updated {README_FILE} with {sum(len(v) for v in grouped_images.values())} wallpapers.")


if __name__ == "__main__":
    main()

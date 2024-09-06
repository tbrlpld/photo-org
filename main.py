import argparse
import datetime
import os
import pathlib
import random
import shutil
import string

from PIL import Image, ExifTags


def main() -> None:
    FILE = pathlib.Path(__file__)
    PROJECT_DIR = FILE.parent
    DATA_DIR = PROJECT_DIR / "data"

    OUT_DIR = PROJECT_DIR / "out"
    # shutil.rmtree(OUT_DIR, ignore_errors=True)

    all_files = DATA_DIR.rglob("*")

    photos = {}
    for f in all_files:
        try:
            p = Photo(source_path=f, destination_dir=OUT_DIR)
        except Photo.UnableToInitializePhoto:
            continue

        dest = p.get_destination_path()
        if dest in photos:
            # Update the filenames to include the original filename. This will help in
            # cases where the original filename had some sensible content to
            # differentiate the images (e.g. a sequence number).

            # Update the existing entry to include original filename.
            existing = photos[dest]
            del photos[dest]
            existing.include_original_filename = True
            existing_dest = existing.get_destination_path()

            # And for the current one, do that too.
            p.include_original_filename = True
            dest = p.get_destination_path()

            # If the filenames are still the same, also include random bits
            if existing_dest == dest:
                existing.randomize_destination_filename = True
                existing_dest = existing.get_destination_path()

                p.randomize_destination_filename = True
                dest = p.get_destination_path()

            photos[existing_dest] = existing

        photos[dest] = p

    for photo in photos.values():
        copy_photo(photo=photo)


class Photo:
    """
    Representation of a photo for moving to a time based file naming.
    """

    ALLOWED_SUFFIXES = [".jpg", ".jpeg", ".JPG", ".JPEG"]

    class UnableToInitializePhoto(Exception):
        pass

    def __init__(self, source_path: pathlib.Path, destination_dir: pathlib.Path) -> None:
        self.path = source_path.resolve()
        self.destination_dir = destination_dir

        self.include_original_filename = False
        self.randomize_destination_filename = False

        if self.path.suffix not in self.ALLOWED_SUFFIXES:
            raise self.__class__.UnableToInitializePhoto(
                f'Suffix "{self.path.suffix}" not allowed.'
            )

        self.image = Image.open(self.path)
        self.exif = self.image.getexif()

        self.created_at: datetime.datetime
        if exif_datetime := self.exif.get(ExifTags.Base.DateTime):
            self.created_at = datetime.datetime.strptime(
                exif_datetime,
                # 2017:06:24 22:05:42
                "%Y:%m:%d %H:%M:%S",
            )
        elif created_timestamp := os.stat(self.path).st_birthtime:
            # This is the initial file creation time on macOS
            self.created_at = datetime.datetime.fromtimestamp(created_timestamp)

    def get_timestamp(self) -> str:
        return self.created_at.strftime("%Y%m%d-%H%M%S")

    def get_destination_filename(self) -> str:
        filename = self.get_timestamp()

        if self.include_original_filename:
            filename = f"{filename}-{self.path.stem}"

        if self.randomize_destination_filename:
            filename = f"{filename}-{get_random_string()}"

        return filename + self.path.suffix

    def get_year(self) -> str:
        return self.created_at.strftime("%Y")

    def get_month(self) -> str:
        return self.created_at.strftime("%m")

    def get_destination_path(self, include_original: bool = False) -> pathlib.Path:
        destination_dir = (
            self.destination_dir
            / self.get_year()
            / self.get_month()
        )

        filename = self.get_destination_filename()
        if include_original:
            filename = self.get_destination_filename(include_original=True)

        destination_file = destination_dir / filename
        return destination_file


def copy_photo(photo: Photo) -> None:
    dest = photo.get_destination_path()

    # Handle duplicates on copy. Even though we avoid clashes in the same script run
    # already, there still could be a file with the same name from a different run.
    # To handle that, we want a random bit in the filename.
    if dest.exists():
        photo.randomize_destination_filename = True
        dest = photo.get_destination_path()

    try:
        shutil.copy2(
            photo.path,
            dest,
        )
    except FileNotFoundError:
        os.makedirs(dest.parent)


def get_random_string() -> str:
    letters_and_digits = string.ascii_lowercase + string.digits
    random_chars = random.choices(letters_and_digits, k=6)
    return "".join(random_chars)


if __name__ == "__main__":
    main()

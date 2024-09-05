import argparse
import datetime
import os
import pathlib
import shutil

from PIL import Image, ExifTags


def main() -> None:
    FILE = pathlib.Path(__file__)
    PROJECT_DIR = FILE.parent
    DATA_DIR = PROJECT_DIR / "data"

    OUT_DIR = PROJECT_DIR / "out"
    shutil.rmtree(OUT_DIR, ignore_errors=True)

    all_files = DATA_DIR.rglob("*")

    for f in all_files:
        try:
            p = Photo(source_path=f, destination_dir=OUT_DIR)
        except Photo.UnableToInitializePhoto:
            pass
        else:
            copy_photo(photo=p)


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
        return self.get_timestamp() + self.path.suffix

    def get_year(self) -> str:
        return self.created_at.strftime("%Y")

    def get_month(self) -> str:
        return self.created_at.strftime("%m")

    def get_destination_path(self) -> pathlib.Path:
        return (
            self.destination_dir
            / self.get_year()
            / self.get_month()
            / self.get_destination_filename()
        )


def copy_photo(photo: Photo) -> None:
    dest = photo.get_destination_path()
    print(dest)
    try:
        shutil.copy2(
            photo.path,
            dest,
        )
    except FileNotFoundError:
        os.makedirs(dest.parent)


if __name__ == "__main__":
    main()

import argparse
import datetime
import os
import pathlib

from PIL import Image, ExifTags


class Photo:
    """
    Representation of a photo for moving to a time based file naming.
    """

    ALLOWED_SUFFIXES = [".jpg", ".jpeg", ".JPG", ".JPEG"]

    class UnableToInitializePhoto(Exception):
        pass

    def __init__(self, path: pathlib.Path) -> None:
        self.path = path.resolve()

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
        elif created_timestamp := os.stat(path).st_birthtime:
            # This is the initial file creation time on macOS
            self.created_at = datetime.datetime.fromtimestamp(created_timestamp)

    def get_timestamp(self) -> str:
        return self.created_at.strftime("%Y%m%d-%H%M%S")

    def get_destination_filename(self) -> str:
        filename = self.get_timestamp()
        return filename + self.path.suffix


def main() -> None:
    FILE = pathlib.Path(__file__)
    PROJECT_DIR = FILE.parent
    DATA_DIR = PROJECT_DIR / "data"

    all_files = DATA_DIR.rglob("*")

    for f in all_files:
        try:
            print(Photo(path=f).get_destination_filename())
        except Photo.UnableToInitializePhoto:
            pass

    # ExifTags.Base.ImageNumber


if __name__ == "__main__":
    main()

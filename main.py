import argparse
import datetime
import os
import pathlib

from PIL import Image, ExifTags


class Photo:
    def __init__(self, path: pathlib.Path) -> None:
        self.path = path
        self.image = Image.open(self.path)
        self.exif = self.image.getexif()

        self.created_at: datetime.datetime
        if exif_datetime := self.exif.get(ExifTags.Base.DateTime):
            # 2017:06:24 22:05:42
            self.created_at = datetime.datetime.strptime(
                exif_datetime,
                "%Y:%m:%d %H:%M:%S",
            )
        elif created_timestamp := os.stat(path).st_birthtime:
            # This is the initial file creation time on macOS
            self.created_at = datetime.datetime.fromtimestamp(created_timestamp)

    def get_timestamp(self) -> str:
        return self.created_at.strftime("%Y%m%d-%H%M%S")


def main() -> None:
    FILE = pathlib.Path(__file__)
    PROJECT_DIR = FILE.parent
    DATA_DIR = PROJECT_DIR / "data"

    jpg_lower = DATA_DIR.rglob("*.jpg")
    jpg_upper = DATA_DIR.rglob("*.JPG")

    photos = list(jpg_lower)
    photos.extend(jpg_upper)

    for p in photos:
        print(Photo(path=p).get_timestamp())


# ExifTags.Base.DateTime
# ExifTags.Base.ImageNumber
# print(datetime.datetime.fromtimestamp(os.stat(p).st_birthtime))


if __name__ == "__main__":
    main()

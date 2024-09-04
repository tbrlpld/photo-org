import argparse
import pathlib

from PIL import Image


def main() -> None:
    FILE = pathlib.Path(__file__)
    PROJECT_DIR = FILE.parent
    DATA_DIR = PROJECT_DIR / "data"

    jpg_lower = DATA_DIR.rglob("*.jpg")
    jpg_upper = DATA_DIR.rglob("*.JPG")

    photos = list(jpg_lower)
    photos.extend(jpg_upper)

    print([p for p in photos])
    for p in photos:
        photo = Image.open(p)
        exif = photo.getexif()
        print(exif)
        # print_exif(exif)


# def print_exif(exif) -> None:
#     for k, v in exif.items():
#       print("Tag", k, "Value", v)



if __name__ == "__main__":
    main()

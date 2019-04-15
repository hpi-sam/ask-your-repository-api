from io import BytesIO
from PIL import Image


class ImageFactory:
    @classmethod
    def load_fixture(cls, file_name, file_format="JPEG"):
        image = Image.open(f"specs/fixtures/{file_name}")
        byte_array = BytesIO()
        image.save(byte_array, format=file_format)
        image.close()

        return BytesIO(byte_array.getvalue())

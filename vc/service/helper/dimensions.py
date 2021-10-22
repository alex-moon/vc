import dotenv


class DimensionsHelper:
    IMAGE_WIDTH_SM = 400
    IMAGE_HEIGHT_SM = 400
    IMAGE_WIDTH_LG = 800
    IMAGE_HEIGHT_LG = 800

    @classmethod
    def width_small(cls):
        return int(
            dotenv.get_key('.env', 'IMAGE_WIDTH_SM')
            or cls.IMAGE_WIDTH_SM
        )

    @classmethod
    def height_small(cls):
        return int(
            dotenv.get_key('.env', 'IMAGE_HEIGHT_SM')
            or cls.IMAGE_HEIGHT_SM
        )

    @classmethod
    def width_large(cls):
        return int(
            dotenv.get_key('.env', 'IMAGE_WIDTH_LG')
            or cls.IMAGE_WIDTH_LG
        )

    @classmethod
    def height_large(cls):
        return int(
            dotenv.get_key('.env', 'IMAGE_HEIGHT_LG')
            or cls.IMAGE_HEIGHT_LG
        )

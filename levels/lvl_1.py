import arcade

from settings import *


class Lvl1:
    @staticmethod
    def on_draw(obj_view):
        # obj_view.camera.use()
        # Draw our Scene
        obj_view.scene.draw()




    @staticmethod
    def layer_options():
        # словарь с параметрами слоев для setup()
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DISAPPEAR_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_LADDERS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_MOVING_DIE_BLOCK: {
                "use_spatial_hash": False,
            },

            LAYER_NAME_CHEST: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_CHECK_POINTS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_SKY: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_GROUND: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_BACKGROUND: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_BACKGROUND2: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DIE_BLOCK: {
                "use_spatial_hash": True,
            },
        }

        return layer_options


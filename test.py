from isaacsim.simulation_app import SimulationApp
simu_app = SimulationApp({"renderer": "RayTracedLighting", "headless": False})

import time
from isaacsim.core.utils import extensions, stage as stage_utils, prims as prims_utils
from pxr import Gf, Sdf, UsdPhysics
from sdg import common


FORK_CAMERA_HEIGHT = 0.75
CAMERA_HEIGHT_TRAIN, CAMERA_HEIGHT_VAL = 0.75, 1.0
CAMERA_RADIUSES_TRAIN = [2.2, 3.2, 4.2]
CAMERA_RADIUSES_VAL = [3.0]
PALLET_WITH_GOODS_COLUMNS = 10


stage_utils.create_new_stage()
prims_utils.create_prim("/World")

environment_prim_path = "/World/Environment"
stage_utils.add_reference_to_stage(
    usd_path="/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Environments/warehouse_trailer.usd",
    prim_path=environment_prim_path
)
common.set_world_trasform(prim=environment_prim_path, translation=[-8.2, 15.1, 0.0], orientation=common.yaw2quat(90.0))
for _ in range(100):
    simu_app.update()

# common.add_colliders(environment_prim_path)

extensions.enable_extension("isaacsim.asset.gen.omap")
import omni.physx, omni.usd, omni.timeline, omni.kit.app
from isaacsim.asset.gen.omap.bindings import _omap as omap_utils
from isaacsim.asset.gen.omap.utils import compute_coordinates,  update_location
import numpy as np
import PIL.Image

# UsdPhysics.Scene.Define(stage_utils.get_current_stage(), Sdf.Path("/World/physicsScene"))

timeline = omni.timeline.get_timeline_interface()


class OccMapGenerator:
    app_interface = omni.kit.app.get_app()
    timeline = omni.timeline.get_timeline_interface()
    omap_interface = omap_utils.acquire_omap_interface()

    def __init__(self, cell_size: float) -> None:
        self.omap_interface.set_cell_size(cell_size)

    def __del__(self):
        omap_utils.release_omap_interface(self.omap_interface)

    def set_transform(self, origin, bound_min, bound_max):
        update_location(self.omap_interface, origin, bound_min, bound_max)

    def generate(self):
        self.omap_interface.update()
        self.app_interface.update()
        self.timeline.play()
        self.app_interface.update()
        self.omap_interface.generate()
        self.app_interface.update()
        self.timeline.stop()

    @property
    def occ_map(self):
        # Format Image
        buffer = self.omap_interface.get_buffer()
        dims = self.omap_interface.get_dimensions()
        buffer = np.array(buffer)
        buffer = np.reshape(buffer, (dims[1], dims[0]))
        occupied_mask = buffer == 1.0
        freespace_mask = buffer == 0.0
        unknown_mask = ~(occupied_mask | freespace_mask)

        unknown_as_freespace = True

        if unknown_as_freespace:
            freespace_mask[unknown_mask] = True
            unknown_mask = np.zeros_like(unknown_mask)

        image = np.zeros(occupied_mask.shape, dtype=np.uint8)
        image[occupied_mask] = 255
        image[unknown_mask] = 255
        # image[freespace_mask] = 255
        return PIL.Image.fromarray(image)





for _ in range(10):
    simu_app.update()

occ_map_generator = OccMapGenerator(cell_size=0.05)


occ_map_generator.set_transform((0.0, 0.0, 0.0),
                                (-10.0, -10.0, 0.1),
                                (10.0, 10.0, 0.9))
occ_map_generator.generate()
occ_map_generator.occ_map.save("omap_1_1.png")

# occ_map_generator.set_transform((-5.2, -11.1, 0.0),
#     (-10.0, -10.0, 0.1),
#     (10.0, 10.0, 0.9))
# occ_map_generator.generate()
# occ_map_generator.occ_map.save("omap_1_2.png")


while simu_app.is_running():
    simu_app.update()
simu_app.close()
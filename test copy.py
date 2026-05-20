from isaacsim.simulation_app import SimulationApp
simu_app = SimulationApp({"renderer": "RayTracedLighting", "headless": True})

import time
from isaacsim.core.utils import extensions, stage as stage_utils, prims as prims_utils
from pxr import Gf, Sdf, UsdPhysics


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
# common.set_world_trasform(prim=environment_prim_path, translation=[-8.2, 15.1, 0.0], orientation=common.yaw2quat(90.0))
# time.sleep(3.0)
for _ in range(100):
    simu_app.update()

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

    def __init__(self, cell_size: float) -> None:
        self._omap_interface = omap_utils.acquire_omap_interface()
        self._omap_interface.set_cell_size(0.05)

    def set_transform(self, origin, bound_min, bound_max):
        update_location(self._omap_interface, origin, bound_min, bound_max)

    def generate(self):
        self._omap_interface.update()
        self.app_interface.update() # type: ignore
        self._omap_interface.generate()
        self.app_interface.update() # type: ignore




for _ in range(10):
    simu_app.update()
physx = omni.physx.get_physx_interface()
stage_id = omni.usd.get_context().get_stage_id()
omap_generator = omap_utils.Generator(physx, stage_id)

omap_generator.update_settings(0.05, 1.0, 0.0, -1.0)
omap_generator.set_transform((-8.2, 15.1, 0.0),
    (-10.0, -10.0, 0.1),
    (10.0, 10.0, 0.9))  # 原点和姿态

simu_app.update()


# Generate occupancy map
timeline.stop()
simu_app.update()
timeline.play()
simu_app.update()

simu_app.update()

omap_generator.generate2d()

simu_app.update()

timeline.stop()

# 获取地图数据
map_data = omap_generator.get_buffer()
map_shape = omap_generator.get_dimensions()
print(f"生成的地图形状: {map_shape}")
# import inspect

# # inspect.ismethod 会自动过滤，只返回 (方法名, 方法对象) 的元组
# methods = inspect.getmembers(omap_generator, predicate=inspect.ismethod)

# # 打印所有函数名字
# for name, _ in methods:
#     print(name)

# omap_generator.use_physx_collision_geometry = False

simu_app.close()
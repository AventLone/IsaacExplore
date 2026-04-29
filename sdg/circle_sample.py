import omni.replicator.core as rep
from isaacsim.core.utils import xforms, stage
import numpy as np
    
class CircleSampler:
    def __init__(self, prim_path: str, frames_required: int) -> None:
        self.obj_prim_path = prim_path
        self.obj_prim = rep.get.prim_at_path(prim_path)

        self.camera = rep.create.camera(focus_distance=400.0, focal_length=2.2,
                                        clipping_range=(0.1, 1000000.0), name="DriverCam")
        
        self.materials = rep.create.material_omnipbr(
            metallic=rep.distribution.uniform(0.0, 1.0),
            roughness=rep.distribution.uniform(0.0, 1.0),
            diffuse=rep.distribution.uniform((0, 0, 0), (1, 1, 1)),
            count=100
        )
        
        rep.randomizer.register(self._randomize_camera_pose)
        rep.randomizer.register(self._randomize_obj_pose)
        rep.randomizer.register(self._randomize_obj_apperance)
        rep.randomizer.register(self._randomize_light)

        self.camera_trigger = rep.trigger.on_frame(max_execs=frames_required, interval=1, rt_subframes=8)
        self.obj_pose_trigger = rep.trigger.on_frame(max_execs=frames_required // 10, interval=10, rt_subframes=8)
        self.obj_apperance_trigger = rep.trigger.on_frame(max_execs=frames_required // 5, interval=5, rt_subframes=8)
        self.light_trigger = rep.trigger.on_frame(max_execs=frames_required // 15, interval=15, rt_subframes=8)

        

    @property
    def obj_position(self):
        position, _ = xforms.get_world_pose(self.obj_prim_path)
        return position

    def trigger_camera(self):
        with self.camera_trigger:
            rep.randomizer._randomize_camera_pose()   # type: ignore

    def trigger_obj_pose(self):
        with self.obj_pose_trigger:
            rep.randomizer._randomize_obj_pose()      # type: ignore

    def trigger_obj_apperance(self):
        with self.obj_apperance_trigger:
            rep.randomizer._randomize_obj_apperance() # type: ignore

    def trigger_light(self):
        with self.light_trigger:
            rep.randomizer._randomize_light()   # type: ignore
    
    def _randomize_obj_pose(self) -> rep.scripts.utils.ReplicatorItem:
        with self.obj_prim:
            rep.modify.pose(position=rep.distribution.uniform((-20.0, -17.0, 0.0), (0.0, -5.0, 0.0)),
                            rotation=rep.distribution.uniform((0, 0, 0), (0, 0, 360)),  # 度
                            scale=rep.distribution.uniform((0.9, 0.9, 0.9), (1.1, 1.1, 1.1)))
        return self.obj_prim.node # type: ignore
    
    def _randomize_obj_apperance(self) -> rep.scripts.utils.ReplicatorItem:
        meshes = rep.get.prims(path_pattern=f"{self.obj_prim_path}/*", prim_types=["Mesh", "GeomSubset"])
        with meshes:
            rep.randomizer.materials(self.materials)
        return meshes.node   # type: ignore

    def _randomize_camera_pose(self) -> rep.scripts.utils.ReplicatorItem:
        with self.camera:
            # a = rep.distribution.uniform((-8.75, -16.6, 0.2), (-5.3, -8.358, 1.2))
            # b = rep.distribution.uniform((-12.945, -17.48, 0.2), (-12.0, -4.65, 1.2))
            # c = rep.distribution.uniform((-18.0, -17.48, 0.2), (-16.6, -4.65, 1.2))
            # rep.modify.pose(
            #     # position=rep.distribution.uniform(*self.camera_position_range),
            #     # position=rep.distribution.uniform((-20.0, -17.0, 0.22), (0.0, -5.0, 1.2)),
            #     position=rep.distribution.choice([a, b, c]),
            #     # look_at=self.obj_prim
            #     rotation=rep.distribution.uniform((-30, -30, 0), (30, 30, 360))  # 度
            # )
            # 核心步骤：
            # position 使用 sequence 依次读取圆周坐标点
            # look_at 确保相机始终对准目标中心
            rep.modify.pose(
                position=rep.distribution.sequence(orbit_pts),
                look_at=self.obj_prim
            )
        return self.camera.node # type: ignore

    def _randomize_light(self) -> rep.scripts.utils.ReplicatorItem:
        lights = rep.get.prims(prim_types=["RectLight", "SphereLight", "DomeLight"])
        with lights:
            rep.modify.attribute("intensity", rep.distribution.uniform(1000, 80000))
            # rep.modify.attribute("temperature", rep.distribution.uniform(3000, 8000))
            rep.modify.attribute("color", rep.distribution.uniform((0.5, 0.5, 0.5), (1.0, 1.0, 1.0)))
        return lights.node # type: ignore
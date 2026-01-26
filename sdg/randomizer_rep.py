import omni.replicator.core as rep
from isaacsim.core.utils import xforms, stage
import numpy as np
    
class Randomizer:
    camera_position_domain_lower = np.array([-3.0, -3.0, 0.1])
    camera_position_domain_upper = np.array([3.0, 3.0, 2.0])

    def __init__(self, prim_path: str, frames_required: int) -> None:
        self.obj_prim_path = prim_path
        self.obj_prim = rep.get.prim_at_path(prim_path)

        self.camera = rep.create.camera(focus_distance=400.0, focal_length=15.0,
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

        self.camera_trigger = rep.trigger.on_frame(max_execs=frames_required, interval=1, rt_subframes=16)
        self.obj_pose_trigger = rep.trigger.on_frame(max_execs=frames_required // 10, interval=10, rt_subframes=16)
        self.obj_apperance_trigger = rep.trigger.on_frame(max_execs=frames_required // 5, interval=5, rt_subframes=16)
        self.light_trigger = rep.trigger.on_frame(max_execs=frames_required // 15, interval=15, rt_subframes=16)

    @property
    def obj_position(self):
        position, _ = xforms.get_world_pose(self.obj_prim_path)
        return position
    
    @property
    def camera_position_range(self):
        return [self.obj_position + Randomizer.camera_position_domain_lower,
                self.obj_position + Randomizer.camera_position_domain_upper]

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
            rep.modify.pose(position=rep.distribution.uniform((-1.0, -1.0, 0.0), (1.0, 1.0, 0.0)),
                            rotation=rep.distribution.uniform((0, 0, 0), (0, 0, 360)),  # 度
                            scale=rep.distribution.uniform((0.9, 0.9, 0.9), (1.1, 1.1, 1.1))
                        )
        return self.obj_prim.node # type: ignore
    
    def _randomize_obj_apperance(self) -> rep.scripts.utils.ReplicatorItem:
        meshes = rep.get.prims(path_pattern=f"{self.obj_prim_path}/*", prim_types=["Mesh", "GeomSubset"])
        with meshes:
            rep.randomizer.materials(self.materials)
        return meshes.node   # type: ignore

    def _randomize_camera_pose(self) -> rep.scripts.utils.ReplicatorItem:
        with self.camera:
            rep.modify.pose(
                position=rep.distribution.uniform(*self.camera_position_range),
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
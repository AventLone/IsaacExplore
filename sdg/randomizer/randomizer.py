import omni.replicator.core as rep
from isaacsim.core.utils import xforms
import numpy as np

FORK_CAMERA_HEIGHT = 0.75

def generate_orbit_positions(origin: np.ndarray, radius: float, count: int):
    # 在 0 到 2pi 之间均匀生成角度
    angles = np.linspace(-np.pi, np.pi, count, endpoint=False)
    # 计算对应的 X, Y 坐标
    return [(float(radius * np.cos(angle) + origin[0]), 
             float(radius * np.sin(angle) + origin[1]), 
             float(origin[2])) for angle in angles]
    
class EventRandomizer:
    
    def __init__(self, prim_path: str, material_count=300) -> None:
        self.obj_prim_path = prim_path
        self.obj_prim = rep.get.prim_at_path(prim_path)
        self.camera = rep.create.camera(focus_distance=400.0, focal_length=15.0,
                                        clipping_range=(0.1, 1000000.0), name="PickupCam")
        
        self._materials = rep.create.material_omnipbr(
            metallic=rep.distribution.uniform(0.0, 1.0),
            roughness=rep.distribution.uniform(0.0, 1.0),
            diffuse=rep.distribution.uniform((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
            count=material_count
        )

        # 3. 定义事件名称
        self._trigger_material_event = "randomize_material"
        self._trigger_camera_event = "randomize_camera_pose"
        self._trigger_light_event = "randomize_light"

        rep.randomizer.register(self._randomize_material)
        rep.randomizer.register(self._randomize_camera_pose)
        rep.randomizer.register(self._randomize_light)

        self._camera_poses = self._get_orbit_points(origin=self.obj_position, radiuses=[1.7, 2.4, 3.1])
        
        self.camera_trigger = rep.trigger.on_custom_event(self._trigger_camera_event)

        with rep.trigger.on_custom_event(self._trigger_material_event):
            rep.randomizer._randomize_material()   # type: ignore
        with self.camera_trigger:
            rep.randomizer._randomize_camera_pose()   # type: ignore
        with rep.trigger.on_custom_event(self._trigger_light_event):
            rep.randomizer._randomize_light()   # type: ignore

    @property
    def frames_generated(self):
        return len(self._camera_poses)

    def randomize_material(self) -> None:
        """外部调用：触发材质随机化"""
        rep.utils.send_og_event(self._trigger_material_event)

    def randomize_camera(self):
        rep.utils.send_og_event(self._trigger_camera_event)

    def randoize_light(self):
        rep.utils.send_og_event(self._trigger_light_event)
       
    @property
    def obj_position(self):
        position, _ = xforms.get_world_pose(self.obj_prim_path)
        return position
    
    def _randomize_material(self) -> rep.scripts.utils.ReplicatorItem:
        meshes = rep.get.prims(path_pattern=f"{self.obj_prim_path}/*", prim_types=["Mesh", "GeomSubset"])
        with meshes:
            rep.randomizer.materials(self._materials)
        return meshes.node   # type: ignore

    def _randomize_camera_pose(self) -> rep.scripts.utils.ReplicatorItem:
        with self.camera:
            rep.modify.pose(
                position=rep.distribution.sequence(self._camera_poses),
                look_at=self.obj_prim
            )
        return self.camera.node # type: ignore

    def _randomize_light(self) -> rep.scripts.utils.ReplicatorItem:
        lights = rep.get.prims(prim_types=["RectLight", "SphereLight", "DomeLight"])
        with lights:
            rep.modify.attribute("intensity", rep.distribution.uniform(1000, 80000))
            rep.modify.attribute("color", rep.distribution.uniform((0.3, 0.3, 0.3), (1.0, 1.0, 1.0)))
        return lights.node # type: ignore
        
    def _get_orbit_points(self, origin: np.ndarray, radiuses: list) -> list:
        positions = list()
        count = 5
        origin[2] = FORK_CAMERA_HEIGHT
        for radius in radiuses:
            positions.extend(generate_orbit_positions(origin, radius, count))
        return positions
        
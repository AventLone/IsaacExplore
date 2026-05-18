import omni.replicator.core as rep
import numpy as np


def generate_orbit_positions(origin: np.ndarray, radius: float, count: int):
    # 在 0 到 2pi 之间均匀生成角度
    angles = np.linspace(0.0, 2.0 * np.pi, count, endpoint=False)
    # 计算对应的 X, Y 坐标
    return [(float(radius * np.cos(angle) + origin[0]), 
             float(radius * np.sin(angle) + origin[1]), 
             float(origin[2])) for angle in angles]

class CameraAndLightRandomizer:
    def __init__(self, camra_height: float, camera_radiuses: list[float]) -> None:
        self.camera = rep.create.camera(focus_distance=400.0, focal_length=15.0,
                                        horizontal_aperture=36.0,  # Increase this value to widen the FOV
                                        clipping_range=(0.1, 1000000.0), name="PickupCam")
        
        # 3. 定义事件名称
        self._trigger_camera_event = "randomize_camera_pose"
        self._trigger_light_event = "randomize_light"

        rep.randomizer.register(self._randomize_camera_pose)
        rep.randomizer.register(self._randomize_light)

        self._camera_poses = CameraAndLightRandomizer.get_orbit_points(height=camra_height, radiuses=camera_radiuses)

        self.camera_trigger = rep.trigger.on_custom_event(self._trigger_camera_event)
    
        with self.camera_trigger:
            rep.randomizer._randomize_camera_pose()   # type: ignore
        with rep.trigger.on_custom_event(self._trigger_light_event):
            rep.randomizer._randomize_light()   # type: ignore

    @property
    def frames_generated(self):
        return len(self._camera_poses)

    def randomize_camera(self):
        rep.utils.send_og_event(self._trigger_camera_event)

    def randomize_light(self):
        rep.utils.send_og_event(self._trigger_light_event)

    def _randomize_camera_pose(self) -> rep.scripts.utils.ReplicatorItem:
        with self.camera:
            rep.modify.pose(
                position=rep.distribution.sequence(self._camera_poses),
                # look_at=self.obj_prim
                look_at=(0.0, 0.0, 0.1)
            )
        return self.camera.node # type: ignore

    def _randomize_light(self) -> rep.scripts.utils.ReplicatorItem:
        lights = rep.get.prims(prim_types=["RectLight", "SphereLight", "DomeLight"])
        with lights:
            rep.modify.attribute("intensity", rep.distribution.choice([1000, 5000, 20000, 40000, 80000]))
            rep.modify.attribute("color", rep.distribution.uniform((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))
        return lights.node # type: ignore

    @staticmethod
    def get_orbit_points(height: float, radiuses: list[float]) -> list:
        points = []
        count = 8
        origin = np.array([0.0, 0.0, height], dtype=np.float32)

        for radius in radiuses:
            points.extend(generate_orbit_positions(origin, radius, count))
        return points
    
class MaterialRandomizer:
    def __init__(self, prim_path: str, material_count=300) -> None:
        self.obj_prim_path = prim_path     
        self._materials = rep.create.material_omnipbr(
            metallic=rep.distribution.uniform(0.0, 1.0),
            roughness=rep.distribution.uniform(0.0, 1.0),
            diffuse=rep.distribution.uniform((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
            count=material_count
        )

        # 3. 定义事件名称
        self._trigger_material_event = "randomize_material"

        rep.randomizer.register(self._randomize_material)

        with rep.trigger.on_custom_event(self._trigger_material_event):
            rep.randomizer._randomize_material()   # type: ignore

    def randomize_material(self) -> None:
        """外部调用：触发材质随机化"""
        rep.utils.send_og_event(self._trigger_material_event)

    def _randomize_material(self) -> rep.scripts.utils.ReplicatorItem:
        meshes = rep.get.prims(path_pattern=f"{self.obj_prim_path}/*", prim_types=["Mesh", "GeomSubset"])
        with meshes:
            rep.randomizer.materials(self._materials)
        return meshes.node   # type: ignore

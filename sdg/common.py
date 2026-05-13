from typing import Sequence
from isaacsim.core.prims import SingleXFormPrim
from isaacsim.core.utils import bounds as bounds_utils, prims as prims_utils
from pxr import Usd, Gf

def yaw2quat(yaw: float) -> Sequence[float]:
    rotation = Gf.Rotation(Gf.Vec3d(0, 0, 1), yaw).GetQuat()
    # Convert Gf.Quat to a format Isaac Sim understands (w, x, y, z)
    # GetReal() is 'w', GetImaginary() is (x, y, z)
    return rotation.GetReal(), *rotation.GetImaginary()

def make_visiable(prim: str | Usd.Prim, visible: bool = True):
    prim = prim if type(prim) is Usd.Prim else prims_utils.get_prim_at_path(prim)
    visibility = "visible" if visible else "invisible"
    prim.GetAttribute("visibility").Set(visibility)

bbox_cache = bounds_utils.create_bbox_cache()

def get_dimensions(prim: str | Usd.Prim):
    """
    Calculate dimensions (x, y, z)
    """
    prim_path = str(prim.GetPrimPath()) if type(prim) is Usd.Prim else prim
    aabb = bounds_utils.compute_aabb(bbox_cache, prim_path) # [min x, min y, min z, max x, max y, max z]
    return float(aabb[3] - aabb[0]), float(aabb[4] - aabb[1]), float(aabb[5] - aabb[2])

def set_local_trasform(prim: str | Usd.Prim, 
                       translation: Sequence[float], 
                       orientation: Sequence[float] = [1.0, 0.0, 0.0, 0.0],
                       scale: Sequence[float] = [1.0, 1.0, 1.0]) -> None:
    prim_path = str(prim.GetPrimPath()) if type(prim) is Usd.Prim else prim
    xform_prim = SingleXFormPrim(prim_path)
    xform_prim.initialize()
    xform_prim.set_local_pose(translation, orientation)
    xform_prim.set_local_scale(scale)

def set_world_trasform(prim: str | Usd.Prim, 
                       translation: Sequence[float], 
                       orientation: Sequence[float] = [1.0, 0.0, 0.0, 0.0],
                       scale: Sequence[float] = [1.0, 1.0, 1.0]) -> None:
    prim_path = str(prim.GetPrimPath()) if type(prim) is Usd.Prim else prim
    xform_prim = SingleXFormPrim(prim_path)
    xform_prim.initialize()
    xform_prim.set_world_pose(translation, orientation)
    xform_prim.set_local_scale(scale)

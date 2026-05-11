from typing import Sequence
from isaacsim.core.prims import SingleXFormPrim
from pxr import Usd


def set_local_trasform(prim: str | Usd.Prim, 
                       translation: Sequence[float], 
                       orientation: Sequence[float] = [1.0, 0.0, 0.0, 0.0],
                       scale: Sequence[float] = [1.0, 1.0, 1.0]) -> None:
    prim_path = str(prim.GetPrimPath()) if type(prim) is Usd.Prim else prim
    xform_prim = SingleXFormPrim(prim_path)
    xform_prim.initialize()
    xform_prim.set_local_pose(translation, orientation)
    xform_prim.set_local_scale(scale)

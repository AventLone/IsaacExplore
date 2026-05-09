"""
Permutations and Combinations
"""
import asyncio, random
from isaacsim.core.utils import prims
from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics
from isaacsim.core.utils import stage, prims, bounds, xforms
from isaacsim.core.prims import SingleXFormPrim
from omni import usd
import numpy as np
from ..randomizer import MaterialRandomizer

bbox_cache = bounds.create_bbox_cache()

def get_dimensions(prim: str | Usd.Prim):
    """
    Calculate dimensions (length, width, height)
    """
    prim_path = str(prim.GetPrimPath()) if type(prim) is Usd.Prim else prim
    aabb = bounds.compute_aabb(bbox_cache, prim_path)
    dimensions = [float(aabb[4] - aabb[1]), float(aabb[3] - aabb[0]), float(aabb[5]- aabb[2])]
    dimensions.sort(reverse=True)
    return tuple(dimensions)


class PermuAndCombi:
    bbox_cache = bounds.create_bbox_cache()
    PRIM_PATH = "/World/CombiPrim"

    def __init__(self, prim_path: str) -> None:
        self.prim = SingleXFormPrim(PermuAndCombi.PRIM_PATH)
        self.prim.initialize()  # needed if you are operating on an existing prim in a scene

        self._component_prim_path = prim_path
        self._stage = stage.get_current_stage()
        _, self._component_width, self._component_height = get_dimensions(prim_path)

        self._colomn_prims = []

        self._trigger = asyncio.Event()
        self._finished = asyncio.Event()
        self._component_number = 0

        self._material_randomizer = MaterialRandomizer(PermuAndCombi.PRIM_PATH)

        prim = prims.get_prim_at_path(prim_path)
        prim.GetAttribute("visibility").Set("invisible")

    def set_pose(self, translation: tuple[float, float, float], yaw: float):
        rotation = Gf.Rotation(Gf.Vec3d(0, 0, 1), yaw).GetQuat()
        # Convert Gf.Quat to a format Isaac Sim understands (w, x, y, z)
        # GetReal() is 'w', GetImaginary() is (x, y, z)
        quat_array = np.array([rotation.GetReal(), *rotation.GetImaginary()])
        self.prim.set_world_pose(position=translation, orientation=quat_array) # type: ignore
        
    @staticmethod
    def make_visiable(prim: str | Usd.Prim, visible: bool = True):
        prim = prim if type(prim) is Usd.Prim else prims.get_prim_at_path(prim)
        visibility = "visible" if visible else "invisible"
        prim.GetAttribute("visibility").Set(visibility)

    def _duplicate(self, path_to: str):
        usd.duplicate_prim(stage=self._stage, prim_path=self._component_prim_path, path_to=path_to)

    def _pile_on(self, colomn_idx: int, row: int):
        """
        Pile a component on top of the specified colomn
        """
        prim_path = f"{PermuAndCombi.PRIM_PATH}/Col{colomn_idx}"
        colomn_prim = prims.get_prim_at_path(prim_path)
        if not colomn_prim.IsValid():
            raise ValueError(f"Colomn prim does not exist at path: {prim_path}")
        
        self._component_number += 1
        component_prim_path = f"{prim_path}/component{self._component_number}"
        self._duplicate(component_prim_path)
        self.make_visiable(component_prim_path)
        new_component_pos = (0.0, 0.0, self._component_height * row)
        prim = SingleXFormPrim(component_prim_path)
        prim.initialize()  # needed if you are operating on an existing prim in a scene
        prim.set_local_pose(translation=new_component_pos)
    
    def _add_colcomn(self, col_idx):
        """
        Add an extra colomn
        """
        self._component_number += 1
        prim_path = f"{PermuAndCombi.PRIM_PATH}/Col{col_idx}"
        self._colomn_prims.append(prims.create_prim(prim_path))
        component_path = f"{prim_path}/component{self._component_number}"
        self._duplicate(component_path)
        self.make_visiable(component_path)
        new_col_pos = (self._component_width * (col_idx - 1), 0.0, 0.0)
        prim = SingleXFormPrim(prim_path)
        prim.initialize()  # needed if you are operating on an existing prim in a scene
        prim.set_local_pose(translation=new_col_pos)

   
    async def run(self, colomns: int, rows=1):
        # while True:
        #     await self._trigger.wait()

        # for _ in range(colomns):
        #     self._add_colcomn()
        #     for _ in range(rows - 1):
        #         self._pile_on(colomn_idx=self._colomn_number)
                
        #         await asyncio.sleep(3.0)
        col_list = list(range(1, colomns + 1))
        random.shuffle(col_list)

        for col in col_list:
            self._add_colcomn(col)
            self._material_randomizer.random_material()
            await asyncio.sleep(1.0)
            for row in range(rows - 1):
                self._pile_on(col, row + 1)
                self._material_randomizer.random_material()
                await asyncio.sleep(1.0)
        
        # prim = SingleXFormPrim(PermuAndCombi.PRIM_PATH)
        # prim.set_visibility(False)




            


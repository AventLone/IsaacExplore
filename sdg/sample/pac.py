"""
Permutations and Combinations
"""
import asyncio, random
from typing import Literal
from isaacsim.core.utils import prims
from pxr import Gf, Usd
from isaacsim.core.utils import stage, prims, bounds
from isaacsim.core.prims import SingleXFormPrim
from omni import usd
from ..randomizer import MaterialRandomizer, stack_boxes_on_pallet_async
from ..common import *

class PermuAndCombi:
    bbox_cache = bounds.create_bbox_cache()
    PRIM_PATH = "/World/CombiPrim"

    def __init__(self, prim_path: str, wait_event=False) -> None:
        self._wait = (lambda: self._trigger.wait()) if wait_event else (lambda: asyncio.sleep(1.0))

        self.prim = SingleXFormPrim(PermuAndCombi.PRIM_PATH)
        self.prim.initialize()  # needed if operating on an existing prim in a scene

        self._component_prim_path = prim_path
        self._stage = stage.get_current_stage()
        self._component_dimensions_x, self._component_dimensions_y, self._component_height = get_dimensions(prim_path)

        self.colomn_prims = []

        self._trigger = asyncio.Event()
        self._finished = asyncio.Event()
        self._component_number = 0

        self._material_randomizer = MaterialRandomizer(PermuAndCombi.PRIM_PATH)

        prim = prims.get_prim_at_path(prim_path)
        prim.GetAttribute("visibility").Set("invisible")

    def set_pose(self, translation: tuple[float, float, float], yaw: float):
        self.prim.set_world_pose(position=translation, orientation=yaw2quat(yaw)) # type: ignore
        
    @staticmethod
    def make_visiable(prim: str | Usd.Prim, visible: bool = True):
        prim = prim if type(prim) is Usd.Prim else prims.get_prim_at_path(prim)
        visibility = "visible" if visible else "invisible"
        prim.GetAttribute("visibility").Set(visibility)

    def _duplicate(self, path_to: str):
        usd.duplicate_prim(stage=self._stage, prim_path=self._component_prim_path, path_to=path_to)

    def _pile_on(self, colomn_idx: int, row: int, xy_range=0.01, yaw_range=5.0):
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
        new_component_pos = (random.uniform(-xy_range, xy_range), 
                             random.uniform(-xy_range, xy_range), 
                             self._component_height * row)

        rotation = Gf.Rotation(Gf.Vec3d(0, 0, 1), random.uniform(-yaw_range, yaw_range)).GetQuat()
        quat_array = [rotation.GetReal(), *rotation.GetImaginary()]
        set_local_trasform(component_prim_path, new_component_pos, quat_array)
    
    def _add_colcomn(self, col_idx, direction: Literal['x', 'y'], gap=0.036):
        """
        Add an extra colomn
        """
        self._component_number += 1
        prim_path = f"{PermuAndCombi.PRIM_PATH}/Col{col_idx}"
        self.colomn_prims.append(prims.create_prim(prim_path))
        component_path = f"{prim_path}/component{self._component_number}"
        self._duplicate(component_path)
        self.make_visiable(component_path)

        new_col_pos = ((self._component_dimensions_x + gap) * (col_idx - 1), 
                       0.0, 0.0) if direction == 'x' else (0.0, (self._component_dimensions_y + gap) * (col_idx - 1), 0.0)
        set_local_trasform(prim_path, new_col_pos)

    async def line_up(self, colomns: int, rows=1, direction: Literal['x', 'y'] = 'x', gap=0.02):
        col_list = list(range(1, colomns + 1))
        random.shuffle(col_list)

        for col in col_list:
            self._add_colcomn(col, direction, gap)
            self._material_randomizer.random_material()
            await self._wait()
            for row in range(rows - 1):
                self._pile_on(col, row + 1)
                self._material_randomizer.random_material()
                await self._wait()

   
    async def run(self, colomns: int, rows=1):
        col_list = list(range(1, colomns + 1))
        random.shuffle(col_list)

        for col in col_list:
            self._add_colcomn(col, 'x')
            self._material_randomizer.random_material()
            await self._wait()
            for row in range(rows - 1):
                self._pile_on(col, row + 1)
                self._material_randomizer.random_material()
                await asyncio.sleep(1.0)

    async def run_stack_boxes(self, colomns: int, boxes_urls_and_weights):
        for col in range(colomns):
            self._add_colcomn(col + 1, 'x')
            num_boxes = random.randint(10, 120)
            await stack_boxes_on_pallet_async(pallet_prim=self.colomn_prims[col],
                                              boxes_urls_and_weights=boxes_urls_and_weights,
                                              num_boxes=num_boxes)




            


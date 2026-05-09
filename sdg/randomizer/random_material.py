import omni.replicator.core as rep

class MaterialRandomizer:
    def __init__(self, prim_path: str, material_count: int = 200) -> None:
        self.obj_prim_path = prim_path 
        # 1. 预创建材质池
        self.materials = rep.create.material_omnipbr(
            metallic=rep.distribution.uniform(0.0, 1.0),
            roughness=rep.distribution.uniform(0.0, 1.0),
            diffuse=rep.distribution.uniform((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
            count=material_count
        )
        
        # 2. 注册随机化逻辑
        rep.randomizer.register(self._randomize_obj_appearance)
        
        # 3. 定义事件名称
        self._trigger_material_event = "trigger_material"
        
        # 4. 关键：直接在初始化时绑定触发器与随机化函数
        # 这样每次事件触发时，register 内部的函数都会被重新执行
        with rep.trigger.on_custom_event(self._trigger_material_event):
            rep.randomizer._randomize_obj_appearance()   # type: ignore

    def random_material(self) -> None:
        """外部调用：触发材质随机化"""
        rep.utils.send_og_event(self._trigger_material_event)

    def _randomize_obj_appearance(self) -> rep.scripts.utils.ReplicatorItem:
        """
        每次触发时都会运行此函数。
        因为写在触发器内，rep.get.prims 会在运行时重新扫描路径下的所有子项。
        """
        meshes = rep.get.prims(
            path_pattern=f"{self.obj_prim_path}/*",
            prim_types=["Mesh", "GeomSubset"],
            cache_result=False,
        )
        with meshes:
            rep.randomizer.materials(self.materials)
        return meshes.node # type: ignore

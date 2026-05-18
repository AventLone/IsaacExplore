import glob
import os

folder_path = "/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/NVIDIA/Assets/Skies"
extension = "hdr"




def find_files(dir: str, extension: str, recursive=True):
    # 拼接匹配模式，** 表示递归匹配任意层级的子文件夹
    search_pattern = os.path.join(folder_path, "**", f"*{extension}")

    # recursive=True 激活多层子文件夹的查找
    return glob.glob(search_pattern, recursive=recursive)

print(len(find_files(folder_path, extension, True)))  # 这是一个包含所有文件路径字符串的列表
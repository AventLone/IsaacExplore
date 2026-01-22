from pathlib import Path

def find_usds(dir: str) -> list[str]:
    folder = Path(dir)
    usd_files = []
    for usd_file in folder.rglob("*.usd"):
        usd_files.append(str(usd_file))
    return usd_files

print(find_usds("/home/avent/Desktop/SimReadyExplorer/Industrial/Pallets"))
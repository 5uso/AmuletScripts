import sys
import amulet
import amulet_nbt
from tqdm import tqdm

def query_yn(question):
    valid = {"yes": True, "y": True, "no": False, "n": False}
    while True:
        print(question, end=" [y/n] ")
        choice = input().lower()
        if choice in valid: return valid[choice]
        else: sys.stdout.write("Please respond with 'yes' or 'no'.\n")

print("\nSpawner primer script by Suso. Using amulet core.\n")

if len(sys.argv) != 2:
    print("Usage: python {} <world>".format(sys.argv[0]))
    exit(0)

if not query_yn("Have you made a backup of your world?"):
    exit(0)

try: level = amulet.load_level(sys.argv[1])
except Exception as e: print("Error loading world:", e)
else:
    for dimension in level.dimensions:
        chunk_coords = sorted(level.all_chunk_coords(dimension))
        if len(chunk_coords) > 0:
            print("Dimension {}:".format(dimension))
            try:
                for coords in tqdm(chunk_coords, unit="chunk"):
                    try: chunk = level.get_chunk(coords[0], coords[1], dimension)
                    except Exception: pass
                    else:
                        for a in chunk.block_entities:
                            if a.base_name == "spawner":
                                a.nbt['utags']['Delay'] = amulet_nbt.TAG_Short(0)
                                chunk.changed = True
                level.save()
            except KeyboardInterrupt:
                print("Interrupted. Changes to this dimension won't be saved.")
                level.close()
                exit(0)
            level.unload()

    level.close()
import amulet, sys, re, os
import amulet_nbt as n
from tqdm import tqdm

OLD_SPAWNER_FORMAT = True # If this is false, uses 1.18+ nbt paths for spawners

REG = re.compile(r'"text" *: *"((?:[^"\\]|\\\\"|\\.)*)"')
REG2 = re.compile(r'\\"text\\" *: *\\"((?:[^"\\]|\\\\.)*)\\"')
CONTAINERS = ["chest", "furnace", "shulker_box", "barrel", "smoker", "blast_furnace", "trapped_chest", "hopper", "dispenser", "dropper", "brewing_stand", "campfire"]

rev_lang = dict()

item_counts = dict()
block_counts = dict()
entity_counts = dict()

key = "no_key"
key_cnt = 0

def query_yn(question):
    valid = {"yes": True, "y": True, "no": False, "n": False}
    while True:
        print(question, end=" [y/n] ")
        choice = input().lower()
        if choice in valid: return valid[choice]
        else: sys.stdout.write("Please respond with 'yes' or 'no'.\n")

def set_key(k):
    global key, key_cnt
    key = k
    key_cnt = 0

def get_key():
    global key_cnt
    key_cnt += 1
    return f"{key}.{key_cnt}"

def match_text(match, escaped = False):
    plain = match.group(1)
    if escaped: plain = re.sub(pattern = r'\\\\', string = plain, repl = r'\\')
    plain = re.sub(pattern = r'\\\\([^\\])', string = plain, repl = r'\\\1')
    plain = re.sub(pattern = r"\\'", string = plain, repl = r"'")
    if plain not in rev_lang: rev_lang[plain] = get_key()
    return f'\\"translate\\":\\"{rev_lang[plain]}\\"' if escaped else f'"translate":"{rev_lang[plain]}"'

def match_text_escaped(match):
    return match_text(match, True)

def replace_component(text):
    text = REG.sub(string = str(text), repl = match_text)
    return n.TAG_String(REG2.sub(string = text, repl = match_text_escaped))

def handle_item(item):
    changed = False
    id = str(item['id'])[10:]
    item_counts.setdefault(id, 1)
    translation_cnt = len(rev_lang)

    try:
        set_key(f"item.{id}.{item_counts[id]}.name")
        item['tag']['display']['Name'] = replace_component(item['tag']['display']['Name'])
        changed = True
    except KeyError: pass

    try:
        for line in range(len(item['tag']['display']['Lore'])):
            set_key(f"item.{id}.{item_counts[id]}.lore.{line}")
            item['tag']['display']['Lore'][line] = replace_component(item['tag']['display']['Lore'][line])
        changed = True
    except KeyError: pass

    try:
        for page in range(len(item['tag']['pages'])):
            set_key(f"item.{id}.{item_counts[id]}.page.{page}")
            item['tag']['pages'][page] = replace_component(item['tag']['pages'][page])
        changed = True
    except KeyError: pass

    try:
        title = item['tag']['title']
        if "display" not in item['tag']: item['tag']['display'] = n.TAG_Compound()
        if "Name" not in item['tag']['display']:
            if title not in rev_lang: rev_lang[title] = f"item.{id}.{item_counts[id]}.title.1"
            item['tag']['display']['Name'] = n.TAG_String(f'{{"translate":"{rev_lang[title]}","italic":false}}')
            changed = True
    except KeyError: pass

    if translation_cnt != len(rev_lang): item_counts[id] += 1

    try: changed |= handle_block_entity_nbt(item['tag']['BlockEntityTag'])
    except KeyError: pass

    try: changed |= handle_entity(item['tag']['EntityTag'], None)
    except KeyError: pass

    return changed

def handle_container(container, type):
    changed = False
    block_counts.setdefault(type, 1)
    translation_cnt = len(rev_lang)

    try:
        set_key(f"block.{type}.{block_counts[type]}.name")
        container['CustomName'] = replace_component(container['CustomName'])
        changed = True
    except KeyError: pass

    if translation_cnt != len(rev_lang): block_counts[type] += 1

    for item in container['Items']: changed |= handle_item(item)

    return changed

def handle_jukebox(jukebox):
    try: return handle_item(jukebox['RecordItem'])
    except KeyError: pass
    return False

def handle_lectern(lectern):
    try: return handle_item(lectern['Book'])
    except KeyError: pass
    return False

def handle_sign(sign):
    block_counts.setdefault("sign", 1)
    translation_cnt = len(rev_lang)

    set_key(f"block.sign.{block_counts['sign']}.text1")
    sign['Text1'] = replace_component(sign['Text1'])
    set_key(f"block.sign.{block_counts['sign']}.text2")
    sign['Text2'] = replace_component(sign['Text2'])
    set_key(f"block.sign.{block_counts['sign']}.text3")
    sign['Text3'] = replace_component(sign['Text3'])
    set_key(f"block.sign.{block_counts['sign']}.text4")
    sign['Text4'] = replace_component(sign['Text4'])

    if translation_cnt != len(rev_lang): block_counts["sign"] += 1

    return True

def handle_entity(entity, type):
    changed = False
    id = type if type is not None else (str(entity['id'])[10:] if "id" in entity else "unknown")
    entity_counts.setdefault(id, 1)
    translation_cnt = len(rev_lang)

    try:
        set_key(f"entity.{id}.{entity_counts[id]}.name")
        entity['CustomName'] = replace_component(entity['CustomName'])
        changed = True
    except KeyError: pass

    if translation_cnt != len(rev_lang): entity_counts[id] += 1

    try:
        for i in entity['Items']: changed |= handle_item(i)
    except KeyError: pass

    try:
        for i in entity['ArmorItems']: changed |= handle_item(i)
    except KeyError: pass

    try:
        for i in entity['HandItems']: changed |= handle_item(i)
    except KeyError: pass

    try:
        for i in entity['Inventory']: changed |= handle_item(i)
    except KeyError: pass

    try:
        for t in entity['Offers']['Recipes']:
            changed |= handle_item(t['buy'])
            changed |= handle_item(t['buyB'])
            changed |= handle_item(t['sell'])
    except KeyError: pass

    try:
        for p in entity['Passengers']: changed |= handle_entity(p, None)
    except KeyError: pass
    return changed

def handle_spawner(spawner):
    changed = False
    try:
        if OLD_SPAWNER_FORMAT:
            changed = handle_entity(spawner['SpawnData'], None)
            for p in spawner['SpawnPotentials']: changed |= handle_entity(p['Entity'], None)
        else:
            changed = handle_entity(spawner['SpawnData']['entity'], None)
            for p in spawner['SpawnPotentials']: changed |= handle_entity(p['data']['entity'], None)
    except KeyError: pass
    return changed

def handle_block_entity_base(block_entity, name):
    if name == "spawner": return handle_spawner(block_entity)
    elif name in CONTAINERS: return handle_container(block_entity, name)
    elif name == "sign": return handle_sign(block_entity)
    elif name == "lectern": return handle_lectern(block_entity)
    elif name == "jukebox": return handle_jukebox(block_entity)
    return False

def handle_block_entity_nbt(block_entity):
    return handle_block_entity_base(block_entity, str(block_entity['id'])[10:])

def handle_block_entity(block_entity):
    return handle_block_entity_base(block_entity.nbt.tag['utags'], block_entity.base_name)

def handle_chunk(chunk):
    for block_entity in chunk.block_entities:
        chunk.changed |= handle_block_entity(block_entity)

def handle_entities(level, coords, dimension, entities):
    changed = False
    for e in entities:
        changed |= handle_entity(e.nbt.tag, e.base_name)
    if changed:
        level.set_native_entites(coords[0], coords[1], dimension, entities)

def scan_world(level):
    for dimension in level.dimensions:
        chunk_coords = sorted(level.all_chunk_coords(dimension))
        if len(chunk_coords) < 1: continue
        print(f"Dimension {dimension}:")
        try:
            count = 0
            for coords in tqdm(chunk_coords, unit = "chunk"):
                try:
                    chunk = level.get_chunk(coords[0], coords[1], dimension)
                    entities = level.get_native_entities(coords[0], coords[1], dimension)[0]
                except Exception: pass
                else:
                    handle_chunk(chunk)
                    handle_entities(level, coords, dimension, entities)
                    count += 1
                    if count < 5000: continue
                    count = 0
                    print()
                    level.save()
                    level.unload()
            level.save()
        except KeyboardInterrupt:
            print("Interrupted. Changes to last 5000 chunk slice won't be saved.")
            level.close()
            exit(0)
        level.unload()
    level.close()

def scan_scores(path):
    try:
        scores = n.load(path)
        for s in scores.tag['data']['Objectives']:
            set_key(f"score.{s['Name']}.name")
            s['DisplayName'] = replace_component(s['DisplayName'])
        for t in scores.tag['data']['Teams']:
            set_key(f"score.{t['Name']}.name")
            t['DisplayName'] = replace_component(t['DisplayName'])
            set_key(f"score.{t['Name']}.prefix")
            t['MemberNamePrefix'] = replace_component(t['MemberNamePrefix'])
            set_key(f"score.{t['Name']}.suffix")
            t['MemberNameSuffix'] = replace_component(t['MemberNameSuffix'])
        scores.save_to(path)
    except Exception as e:
        print("No scoreboard data could be accessed:", e)

def scan_level(path):
    try:
        level = n.load(path)
        for b in level.tag['Data']['CustomBossEvents']:
            set_key(f"bossbar.{b}.name")
            level.tag['Data']['CustomBossEvents'][b]['Name'] = replace_component(level.tag['Data']['CustomBossEvents'][b]['Name'])
        level.save_to(path)
    except Exception as e:
        print("No bossbar data could be accessed:", e)

def scan_structure(path):
    try:
        structure = n.load(path)
        for b in structure.tag['blocks']:
            try: handle_block_entity_nbt(b['nbt'])
            except KeyError: pass
        for e in structure.tag['entities']: 
            try: handle_entity(e['nbt'], None)
            except KeyError: pass
        structure.save_to(path)
    except Exception as e:
        print("Couldn't open structure file '" + path + "':", e)

def scan_file(path, start):
    if path.endswith(".nbt"):
        scan_structure(path)
        return
    if not path.endswith(".mcfunction") and not path.endswith(".json"):
        return
    try:
        k = path[start:]
        k = k[k.find("\\data\\") + 6:]
        k = k.replace("\\", ".")
        k = k[:-11] if k.endswith(".mcfunction") else k[:-5]
        set_key(k)
        with open(path, 'r', encoding = "utf-8") as f:
            txt = REG.sub(string = f.read(), repl = match_text)
            txt = REG2.sub(string = txt, repl = match_text_escaped)
        with open(path, 'w', encoding = "utf-8") as f:
            f.write(txt)
    except Exception as e:
        print("Can't replace datapack file '" + path + "':", e)

def scan_datapacks(path):
    for root, _, files in os.walk(path):
        for f in files:
            scan_file(os.path.join(root, f), len(path) + 1)

def gen_lang(path):
    with open(path, 'w', encoding = "utf-8") as f:
        f.write('{\n')
        lines = list(map(lambda entry: f'  "{rev_lang[entry]}": "{entry}",\n', rev_lang))
        if len(lines) == 0: print("No translatable text found")
        else: lines[-1] = lines[-1][:-2]
        f.writelines(lines)
        f.write('\n}\n')

def main():
    print("\nWorld Translation Extractor, by Suso. Using amulet core.\n")

    if len(sys.argv) != 2:
        print("Usage: python {} <world>".format(sys.argv[0]))
        exit(0)

    if not query_yn("Have you made a backup of your world?"):
        exit(0)

    rev_lang[""] = "empty"

    print("\nScanning chunks...")
    try:
        level = amulet.load_level(sys.argv[1])
        scan_world(level)
    except Exception as e:
        print("Error loading world:", e)
        exit(1)

    print("\nScanning misc NBT...")
    scan_scores(sys.argv[1] + "/data/scoreboard.dat")
    scan_level(sys.argv[1] + "/level.dat")

    print("\nScanning datapack files...")
    scan_datapacks(sys.argv[1] + "/datapacks")
    scan_datapacks(sys.argv[1] + "/generated")

    print("\nGenerating default lang file...")
    gen_lang('default_lang.json')

    print("Done!")

if __name__ == '__main__':
    main()

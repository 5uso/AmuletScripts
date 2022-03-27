import sys
import amulet
import amulet_nbt
from tqdm import tqdm

DO_ENCHANTS = True
DO_ABILITIES = True

CARTO_ENCHANTS = {
    "Loyalty": 'loyalty',
    "Thorns": 'thorns',
    "Adrenaline": 'adrenaline',
    "Agility": 'agility',
    "Aquadynamic": 'aquadynamic',
    "Concealed": 'concealed',
    "FatigueCleansing": 'fatigue_cleansing',
    "SlownessCleansing": 'slowness_cleansing',
    "WeaknessCleansing": 'weakness_cleansing',
    "PoisonCleansing": 'poison_cleansing',
    "WitherCleansing": 'wither_cleansing',
    "Energetic": 'energetic',
    "Evasion": 'evasion',
    "Frenzy": 'frenzy',
    "Lifesteal": 'lifesteal',
    "Rally": 'rally',
    "Regeneration": 'regeneration',
    "Satiation": 'satiation',
    "SecondWind": 'second_wind',
    "Soulbound": 'soulbound',
    "Spurs": 'spurs',
    "Commited": 'exposing',
    "Decay": 'infection',
    "Duelist": 'duelist',
    "Echo": 'echo',
    "Evocation": 'evocation',
    "Executioner": 'executioner',
    "Frostbite": 'frostbite',
    "Hunter": 'hunter',
    "Overload": 'electrocute',
    "Stunning": 'stunning',
    "SurgingStrike": 'surging_strike',
    "Transfiguration": 'transfiguration',
    "Vanquisher": 'unchanting',
    "Vicious": 'bleeding',
    "Conductive": 'electrode',
    "Frost": 'frost',
    "Flash": 'flash',
    "PinDown": 'expose',
    "PointBlank": 'point_blank',
    "Putrefy": 'infect',
    "Sharpshot": 'sharpshot',
    "AutoCharge": 'auto_charge',
    "Deadeye": 'deadeye',
    "Repeating": 'repeating',
    "Rend": 'bleed',
    "TempoTheft": 'tempo_theft',
    "Trueshot": 'trueshot',
    "Volatile": 'explosive',
    "Current": 'current',
    "Hydraulic": 'hydraulic',
    "Ricochet": 'ricochet',
    "Tempest": 'tempest',
    "Eruption": 'eruption',
    "Sapper": 'sapper',
    "Splintering": 'splintering',
    "Infinity": 'infinity',
    "CurseEncumbering": 'curse_encumbering',
    "CurseMalevolence": 'curse_malevolence',
    "CurseRegret": 'curse_regret',
    "CurseShattering": 'curse_shattering',
    "CurseTwoHanded": 'curse_two_handed'
}
CARTO_LORES = {
    "\"Rend ": "\"Bleed ",
    "\"Vicious ": "\"Bleeding ",
    "\"Overload ": "\"Electrocute ",
    "\"Conducive ": "\"Electrode ",
    "\"Decay ": "\"Infection ",
    "\"Putrefy ": "\"Infect ",
    "\"Commited ": "\"Exposing ",
    "\"Pin Down ": "\"Expose ",
    #"\"Volatile ": "\"Explosive "
}
CARTO_ABILITIES = {
    "has_active": ["ca.has_active"],
    "ambush": ["ca.ambush"],
    "augmenter": ["ca.augmenter"],
    "charge": ["ca.charge"],
    "cloaker": ["ca.cloaker"],
    "disarm": ["ca.disarm"],
    "duplicator": ["ca.duplicator", "ca.triple"],
    "fireball": ["ca.magic_missile", "ca.blazing"],
    "flame_nova": ["ca.nova", "ca.blazing"],
    "frost_nova": ["ca.nova", "ca.glacial"],
    "healer": ["ca.healer"],
    "hookshot": ["ca.hookshot"],
    "laser": ["ca.laser"],
    "magic_missile": ["ca.magic_missile"],
    "smash": ["ca.smash"],
    "recast": ["ca.recast"],
    "rerecast": ["ca.rerecast"],
    "soulfire_nova": ["ca.nova", "ca.celestial"],
    "sweep": ["ca.sweep"],
    "mobile": ["ca.mobile"],
    "unstoppable": ["ca.unstoppable"],
    "trapper": ["ca.trapper"],
    "venom_nova": ["ca.nova", "ca.venemous"],
    "wind_nova": ["ca.nova", "ca.zephyrous"],
    "webshot": ["ca.webshot"],
    "wither_storm": ["ca.wither_storm"],
    "corpse_crawler": ["ca.corpse_crawler"],
    "corpse_crawler_husk": ["ca.corpse_crawler_husk"],
    "corpse_crawler_drowned": ["ca.corpse_crawler_drowned"],
    "corpse_crawler_piglin": ["ca.corpse_crawler_piglin"],
    "corpse_crawler_zoglin": ["ca.corpse_crawler_zoglin"],
    "corpse_crawler_bee": ["ca.corpse_crawler_bee"],
    "corpse_crawler_spider": ["ca.corpse_crawler_spider"],
    "exalted": ["ca.exalted"],
    "parting_gift": ["ca.parting_gift"],
    "pyromania": ["ca.pyromania"],
    "spectral": ["ca.spectral"],
    "brutal_blood": ["ca.brutal_blood"],
    "relentless_blood": ["ca.relentless_blood"],
    "devious_blood": ["ca.devious_blood"],
    "sacrificial_blood": ["ca.sacrificial_blood"],
    "breaker": ["ca.breaker"],
    "enderport": ["ca.enderport"],
    "permacloak": ["ca.shimmerskin"],
    "reflect_ranged": ["ca.reflect_ranged"],
    "reflect_melee": ["ca.reflect_melee"],
    "quiver": ["ca.quiver"]
}

def query_yn(question):
    valid = {"yes": True, "y": True, "no": False, "n": False}
    while True:
        print(question, end=" [y/n] ")
        choice = input().lower()
        if choice in valid: return valid[choice]
        else: sys.stdout.write("Please respond with 'yes' or 'no'.\n")

def handle_container(chunk, container):
    for item in container.nbt['utags']['Items']:
        item_changed = False
        for ench in CARTO_ENCHANTS:
            try:
                lvl = item['tag'][ench]
                if 'CustomEnchantments' not in item['tag']:
                    item['tag']['CustomEnchantments'] = amulet_nbt.TAG_List([])
                item['tag']['CustomEnchantments'].append(amulet_nbt.TAG_Compound({
                    "id": amulet_nbt.TAG_String(CARTO_ENCHANTS[ench]),
                    "lvl": amulet_nbt.TAG_Byte(lvl)
                }))
                item_changed = True
                chunk.changed = True
            except KeyError: pass
        if item_changed:
            try:
                for i in range(len(item['tag']['display']['Lore'])):
                    s = str(item['tag']['display']['Lore'][i])
                    for o, r in CARTO_LORES.items(): s = s.replace(o, r)
                    if "\"Volatile " in s: s = "{\"italic\":false,\"color\":\"gray\",\"text\":\"Explosive\"}"
                    item['tag']['display']['Lore'][i] = amulet_nbt.TAG_String(s)
            except KeyError: pass

def handle_mob(chunk, mob):
    try:
        for i in range(len(mob['Tags'])):
            prev_tag = str(mob['Tags'][i])
            if prev_tag in CARTO_ABILITIES:
                new_tags = CARTO_ABILITIES[prev_tag]
                mob['Tags'][i] = amulet_nbt.TAG_String(new_tags[0])
                for i in range(1, len(new_tags)): mob['Tags'].append(amulet_nbt.TAG_String(new_tags[i]))
                chunk.changed = True
    except KeyError: pass
    try:
        for p in mob['Passengers']: handle_mob(chunk, p)
    except KeyError: pass

def main():
    print("\nCarto updater script by Suso. Using amulet core.\n")

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
                                if DO_ENCHANTS and a.base_name in ["chest", "furnace", "shulker_box", "barrel", "smoker", "blast_furnace", "trapped_chest", "hopper", "dispenser", "dropper"]:
                                    handle_container(chunk, a)
                                if DO_ABILITIES and a.base_name == "spawner":
                                    handle_mob(chunk, a.nbt['utags']['SpawnData'])
                                    for p in a.nbt['utags']['SpawnPotentials']: handle_mob(chunk, p['Entity'])
                    level.save()
                except KeyboardInterrupt:
                    print("Interrupted. Changes to this dimension won't be saved.")
                    level.close()
                    exit(0)
                level.unload()
        level.close()

if __name__ == '__main__':
    main()

# AmuletScripts
Small utility scripts for editing minecraft worlds using https://github.com/Amulet-Team/Amulet-Core.

Tested with Python 3.9, Minecraft 1.18. Should work with any Python 3 and any version of Minecraft supported by amulet (currently 1.12-1.18).

_**Please, create backups of your worlds before running external tools to modify them.**_

## Spawner Primer
Sets the `Delay` tag of all of the mob spawners in a given world to `0s`.

Usage: `python SpawnerPrimer.py <world>`

Dependencies: `pip install amulet-map-editor` `pip install tqdm`

## Cartographer Updater
Updates enchantments and mob ability tags from old [cartographer](https://github.com/pearuhdox/Cartographer) versions.

Usage: `python CartoUpdater.py <world>`

Dependencies: `pip install amulet-map-editor` `pip install tqdm`

## World Translation Extractor
Scans a full world searching for json `"text"` components and replaces them with `"translation"` components, generating a lang file to be used with a resourcepack. Tested in `1.16.5` and `1.19.3`.

Finds json components in:
- Blocks
  - Spawners: SpawnData, SpawnPotentials
  - Containers: items, container name (`"chest"`, `"furnace"`, `"shulker_box"`, `"barrel"`, `"smoker"`, `"blast_furnace"`, `"trapped_chest"`, `"hopper"`, `"dispenser"`, `"dropper"`, `"brewing_stand"`, `"campfire"`)
  - Signs: text1-4
  - Lecterns: Book
  - Jukeboxes: RecordItem

- Entities
  - Name
  - Items
  - ArmorItems
  - HandItems
  - Inventory
  - Villager offers
  - Passengers

- Items
  - Name
  - Lore
  - Book pages
  - Book title: adds a customname in case it doesn't already have one
  - BlockEntityTag
  - EntityTag:

- Scoreboard: objective names, team names and affixes

- Bossbars: names

- Datapacks: functions, json files

- Structures: blocks, entities

Usage: `python WorldTranslationExtractor.py <world>` (Modifies world, outputs `default_lang.json` in the working directory)

Dependencies: `pip install amulet-map-editor` `pip install tqdm`

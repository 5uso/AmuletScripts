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

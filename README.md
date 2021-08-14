# Blender to NBT
A collection of Blender scripts to aid in the creation and exporting of Structure Block NBT files, for use in minecraft. 

These can be used to make structures using vanilla [Structure Blocks](https://minecraft.fandom.com/wiki/Structure_Block), the [Create mod](https://www.curseforge.com/minecraft/mc-mods/create) as files for the [Schematicannon](https://create.fandom.com/wiki/Schematicannon) or any other mods, plugins or external programs which use the [Structure Block NBT file format](https://minecraft.fandom.com/wiki/Structure_Block_file_format).

## Downloads

You can download both addons from the [releases tab](https://github.com/underscoren/blender-to-nbt/releases)

## Usage

The addons come in two parts, designed to be used with each other. The first addon is `voxelize-exact.py`, which adds a new operator to objects that attempts to create exact 1m cubes using the remesh modifier. You can find it at the bottom of the Obeject menu listed as Voxelize Exact.

The second part is the `nbt-export` addon, which scans the currently selected object for blocks, and exports them to an NBT file. You can find it under File > Export > NBT Structure File (.nbt).

The export script has some caveats, namely that it expects blocks to be 1m in size and on meter increments. The `voxelize-exact` addon should produce the blocks the export script expects.

## License

The code in this repository is licensed under the [MIT License](LICENSE.md). The python [NBT library](https://github.com/twoolie/NBT) used is also licensed under [MIT](nbt-export/nbt/LICENSE.txt).
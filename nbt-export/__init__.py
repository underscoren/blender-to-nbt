bl_info = {
    "name": "NBT Export",
    "description": "Exports the selected object to an nbt structure file",
    "author": "_n#1111",
    "location": "File > Export > NBT Export",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "category": "Import-Export",
}

import bpy
from mathutils import Vector
from .nbt import nbt

def export_nbt(context, file_path, block_name):
    object = context.active_object

    dimX = object.dimensions.x
    dimY = object.dimensions.y
    dimZ = object.dimensions.z

    minX = minY = minZ = float( "inf")
    maxX = maxY = maxZ = float("-inf")

    # find the minimum and maximum coordinates of the object in world-space
    bbox_corners = [object.matrix_world @ Vector(corner) for corner in object.bound_box]

    for point in bbox_corners:
        minX = min(minX, round(point.x))
        minY = min(minY, round(point.y))
        minZ = min(minZ, round(point.z))

        maxX = max(maxX, round(point.x))
        maxY = max(maxY, round(point.y))
        maxZ = max(maxZ, round(point.z))

    blocks = []

    # naive raycasting block-finder
    # not very efficient, but it's fast enough to not notice unless you've got a massive model

    # get matrices for convenience
    wm = object.matrix_world
    inv_wm = object.matrix_world.inverted()

    print("scanning for blocks")

    for z in range(int(minZ), int(maxZ)):
        #print("z", z)
        for y in range(int(minY), int(maxY)):
            x = minX - 0.5 # first plane may be too close to hit by raycast
            while x < maxX:
                start = Vector((x, y+0.5, z+0.5))
                dir = Vector((1,0,0))

                # convert to object-space coordinates
                start = inv_wm @ start

                result, point, _, _ = object.ray_cast(start, dir, distance=(maxX-x))

                if result:
                    # convert back to world-space coordinates
                    point = wm @ point
                    start_x = point[0]

                    # find end coordinates of block(s)
                    start = inv_wm @ Vector((start_x+0.5, y+0.5, z+0.5)) # need to add 0.5 to not hit the same plane again
                    result, point, _, _ = object.ray_cast(start, dir)

                    if not result:
                        raise Exception("Could not find end plane starting at point "+ str((start_x+0.5, y+0.5, z+0.5)))

                    point = wm @ point
                    end_x = point[0]

                    block_line = [(x, z, -y) for x in range(int(round(start_x)), int(round(end_x)))]
                    blocks += block_line

                    x = end_x + 0.5
                else:
                    break # no more blocks exist on this line
                

    print("done")
    print(len(blocks), "blocks")

    minX = minY = minZ = float("inf")

    for block in blocks:
        minX = min(minX, block[0])
        minY = min(minY, block[1])
        minZ = min(minZ, block[2])

    # translate all blocks to start at 0,0,0
    blocks = [(p[0] - minX, p[1] - minY, p[2] - minZ) for p in blocks]


    # save blocks as structure nbt

    nbtfile = nbt.NBTFile()

    dataVersion = nbt.TAG_Int(name="DataVersion", value=2730)

    sizeList = nbt.TAG_List(name="size", type=nbt.TAG_Int)

    for num in [dimX, dimY, dimZ]:
        sizeList.tags.append(nbt.TAG_Int(int(round(num))))

    palette = nbt.TAG_List(name="palette", type=nbt.TAG_Compound)

    block = nbt.TAG_Compound()
    block.tags.append(nbt.TAG_String(name="Name", value=block_name))

    palette.tags.append(block)
    entities = nbt.TAG_List(name="entities", type=nbt._TAG_End)

    blockListTag = nbt.TAG_List(name="blocks", type=nbt.TAG_Compound)

    for block in blocks:
        blockTag = nbt.TAG_Compound()
        posTag = nbt.TAG_List(name="pos", type=nbt.TAG_Int)

        for p in block:
            posTag.tags.append(nbt.TAG_Int(p))

        stateTag = nbt.TAG_Int(name="state", value=0)

        blockTag.tags.append(posTag)
        blockTag.tags.append(stateTag)

        blockListTag.tags.append(blockTag)


    for tag in [dataVersion, sizeList, palette, entities, blockListTag]:
        nbtfile.tags.append(tag)

    nbtfile.write_file(file_path)


from bpy_extras.io_utils import ExportHelper

class EXPORT_OBJECT_OT_nbt(bpy.types.Operator, ExportHelper):
    """Export selected object as nbt structure block format. Model must consist of axis-aligned 1-meter cubes"""
    bl_idname = "export_object.nbt"
    bl_label = "Export NBT"

    filename_ext = ".nbt"

    filter_glob: bpy.props.StringProperty(
        default="*.nbt",
        options={"HIDDEN"},
        maxlen=255,
    )

    block_name: bpy.props.StringProperty(
        name="Block id",
        description="Namespaced block ID",
        default="minecraft:stone",
    )

    def execute(self, context):
        export_nbt(context, self.filepath, self.block_name)
        return {"FINISHED"}


def menu_func_export(self, context):
    self.layout.operator(EXPORT_OBJECT_OT_nbt.bl_idname, text="NBT Structure File (.nbt)")


def register():
    bpy.utils.register_class(EXPORT_OBJECT_OT_nbt)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(EXPORT_OBJECT_OT_nbt)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

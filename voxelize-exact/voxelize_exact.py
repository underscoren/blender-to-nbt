bl_info = {
    "name": "Voxelize Exact",
    "description": "Turn an object into meter-size cubes.",
    "author": "_n#1111",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Object",
    "category": "Object"
}

import bpy
from math import log, ceil


def voxelize_exact(context, accuracy, report):
    object = context.active_object
    largest_dim = max(list(object.dimensions))
    
    bpy.ops.object.modifier_add(type="REMESH")
    mod = object.modifiers["Remesh"]
    mod.mode = "BLOCKS"
    mod.octree_depth = accuracy
    
    scale = largest_dim/(2**accuracy)
    mod.scale = scale
    
    if scale > 1:
        report(
            {"WARNING"}, 
            f"Accuracy too small to make exact meter cubes. Must be at least {ceil(log(largest_dim, 2))}"
        )
    
    bpy.ops.object.modifier_apply(modifier="Remesh")
    context.view_layer.update()
    
    # make the vertices line up on global integer increments
    vert = object.matrix_world @ object.data.vertices[0].co

    object.location.x += (vert.x % 1) * (1 if vert.x > 0 else -1)
    object.location.y += (vert.y % 1) * (1 if vert.y > 0 else -1)
    object.location.z += (vert.z % 1) * (1 if vert.z > 0 else -1)

    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)



class OBJECT_OT_voxelize_exact(bpy.types.Operator):
    """Voxelize object into meter cubes"""
    bl_idname = "object.voxelize_exact"
    bl_label = "Voxelize Exact"
    bl_options = {"REGISTER", "UNDO"}
    
    accuracy: bpy.props.IntProperty(
        name="Accuracy",
        description="Controls remesh octree depth",
        min=1, soft_max=10,
        default=7,
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        voxelize_exact(context, self.accuracy, self.report)
        return {"FINISHED"}

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_voxelize_exact.bl_idname)


def register():
    bpy.utils.register_class(OBJECT_OT_voxelize_exact)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_voxelize_exact)
    bpy.types.VIEW3D_MT_add.remove(menu_func)

if __name__ == "__main__":
    register()

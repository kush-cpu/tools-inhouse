import bpy

class ExportShaderSetupPanel(bpy.types.Panel):
    bl_label = "Export Shader Setup"
    bl_idname = "PT_export_shader_setup"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene, "export_shader_setup_source_file_path")
        layout.prop(context.scene, "export_shader_setup_target_file_path")
        layout.prop(context.scene, "export_shader_setup_source_material_name")
        layout.prop(context.scene, "export_shader_setup_target_material_name")

        layout.operator("script.export_shader_setup_operator")

class ExportShaderSetupOperator(bpy.types.Operator):
    bl_idname = "script.export_shader_setup_operator"
    bl_label = "Export Shader Setup"

    def execute(self, context):
        source_blend_path = bpy.path.abspath(context.scene.export_shader_setup_source_file_path)
        target_blend_path = bpy.path.abspath(context.scene.export_shader_setup_target_file_path)
        source_material_name = context.scene.export_shader_setup_source_material_name
        target_material_name = context.scene.export_shader_setup_target_material_name

        with bpy.data.libraries.load(source_blend_path) as (data_from, data_to):
            data_to.materials = [name for name in data_from.materials if name == source_material_name]

        with bpy.data.libraries.load(target_blend_path) as (data_from, data_to):
            data_to.materials = [name for name in data_from.materials if name == target_material_name]

        source_material = bpy.data.materials[source_material_name]
        target_material = bpy.data.materials[target_material_name]

        if source_material and target_material:
            target_material.node_tree.nodes.clear()
            for node in source_material.node_tree.nodes:
                new_node = target_material.node_tree.nodes.new(type=node.bl_idname)
                new_node.name = node.name
                new_node.location = node.location
                if hasattr(node, 'inputs'):
                    for input in node.inputs:
                        if input.is_linked:
                            for link in input.links:
                                new_node.inputs[input.name].links.new(link.from_socket)
                        else:
                            new_node.inputs[input.name].default_value = input.default_value
                if hasattr(node, 'outputs'):
                    for output in node.outputs:
                        if output.is_linked:
                            for link in output.links:
                                target_material.node_tree.links.new(new_node.outputs[output.name], link.to_socket)

            bpy.ops.wm.save_as_mainfile(filepath=target_blend_path)

        return {'FINISHED'}

classes = [
    ExportShaderSetupPanel,
    ExportShaderSetupOperator
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.export_shader_setup_source_file_path = bpy.props.StringProperty(name="Source File Path", default="")
    bpy.types.Scene.export_shader_setup_target_file_path = bpy.props.StringProperty(name="Target File Path", default="")
    bpy.types.Scene.export_shader_setup_source_material_name = bpy.props.StringProperty(name="Source Material Name", default="")
    bpy.types.Scene.export_shader_setup_target_material_name = bpy.props.StringProperty(name="Target Material Name", default="")

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.export_shader_setup_source_file_path
    del bpy.types.Scene.export_shader_setup_target_file_path
    del bpy.types.Scene.export_shader_setup_source_material_name
    del bpy.types.Scene.export_shader_setup_target_material_name

if __name__ == "__main__":
    register()

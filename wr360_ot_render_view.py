'''
Copyright (C) WebRotate 360 LLC
support@webrotate360.com
'''

import os
import bpy
from bpy.utils import register_class, unregister_class

class WR360_OT_RenderView(bpy.types.Operator):
    bl_idname = 'wr360.render_view'
    bl_label = 'Build Target'
    bl_description = 'Render images and run selected command'

    def execute(self, context):   
        wr360Config = context.scene.wr360Config
        context.scene.wr360State.switch_to_object_mode()
        
        wr360Publisher = context.scene.wr360Publisher
        proj_name = os.path.basename(os.path.normpath(wr360Config.out_dir))
        
        if wr360Config.command == 'publish_view' or wr360Config.command == 'publish_view_launch':
            assets_folder = os.path.join('published', '360_assets', proj_name)
            if wr360Config.skip_render:
                wr360Publisher.update_view(context, assets_folder)
                return {'FINISHED'}    
            wr360Publisher.render_view(context, assets_folder)
        elif wr360Config.command == 'publish_project' or wr360Config.command == 'publish_project_launch':
            if wr360Config.skip_render:
                wr360Publisher.update_project(context, '')
                return {'FINISHED'}    
            wr360Publisher.render_project(context, '')
        elif wr360Config.command == 'no_publish':
            wr360Publisher.render(context, '_render')
      
        return {'FINISHED'}      
    
def register():
    register_class(WR360_OT_RenderView)

def unregister():
    unregister_class(WR360_OT_RenderView)        
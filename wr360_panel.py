'''
Copyright (C) WebRotate 360 LLC
support@webrotate360.com
'''

import bpy
from bpy.types import Panel
from bpy.utils import register_class, unregister_class

class WR360_PT_Panel(Panel):
    bl_label = 'WebRotate 360'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    
    def draw(self, context):
        wr360Config = context.scene.wr360Config 
        
        scene = context.scene
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        row = layout.row()
        col = row.column()
        col.prop(wr360Config, 'out_dir')
        
        #row = layout.row()
        #col = row.column()
        #col.prop(wr360Config, 'proj_name')
        #if scene.wr360Config.out_dir == '':
        #    col.enabled = False
        
        row = layout.row()
        col = row.column()
        #col.prop(context.view_layer.objects, 'active')
        col.prop(scene.wr360Config, 'active_object')
      
        selected_obj = scene.wr360Config.active_object 
        if not scene.wr360Config.out_dir: #or not scene.wr360Config.proj_name:
            col.enabled = False
        
        row = layout.row()
        row.operator('wm.url_open', text='Help', icon='QUESTION').url = "https://www.webrotate360.com/products/cms-and-e-commerce-plugins/plugin-for-blender.aspx"    
        
        boxSetup = layout.box()
        boxSetup.label(text='Animation')
        col = boxSetup.column(align=True)
        col.prop(scene.wr360Config, 'frame_number')
        col.prop(scene.wr360Config, 'vertical_row_up')
        col.prop(scene.wr360Config, 'vertical_row_down')
        col.prop(scene.wr360Config, 'vertical_angle_step')        
        col = boxSetup.column()
        col.prop(scene.wr360Config, 'horiz_dir_clockwise')    
        
        row = boxSetup.row()
        row.scale_y = 1.5
        row.operator('wr360.animate', icon='OUTLINER_OB_CAMERA')
        row = boxSetup.row()
        row.scale_y = 1.5
        row.operator('wr360.to_setup_frame', icon='LOOP_BACK')
        
        boxCamera = layout.box()
        boxCamera.label(text='Camera')
        col = boxCamera.column(align=True)
        col.prop(scene.wr360Config, 'cam_distance')
        col.prop(scene.wr360Config, 'cam_focal_length')
        col.prop(scene.wr360Config, 'x_resolution')
        col.prop(scene.wr360Config, 'y_resolution')
       
        boxRender = layout.box()
        boxRender.label(text='Render and view')
        col = boxRender.column()
        col.prop(scene.wr360Config, 'viewer_skin')
        col.prop(scene.wr360Config, 'viewer_background')
        col.prop(scene.wr360Config, 'first_frame')
        
        col = boxRender.column()
        col.prop(scene.wr360Config, 'flip_vert_input')
        if scene.wr360Config.vertical_row_down == 0 and scene.wr360Config.vertical_row_up == 0:
            col.enabled = False
        
        col = boxRender.column()
        col.prop(scene.wr360Config, 'image_format')
        if scene.wr360Config.image_format == 'jpg':
            col.prop(scene.wr360Config, 'image_quality')
        
        col = boxRender.column()
        col.prop(scene.wr360Config, 'fast_render')    
        
        sub = col.column(align=True)
        sub.prop(scene.wr360Config, 'render_region')
        sub.active = scene.wr360Config.fast_render is False
        
        sub = col.column(align=True)
        sub.active = scene.wr360Config.fast_render is False and scene.wr360Config.render_region is True
        sub.prop(scene.wr360Config, 'crop_region')
        
        sub = col.column(align=True)
        sub.prop(scene.wr360Config, 'skip_render')
        
        col = boxRender.column()
        col.prop(scene.wr360Config, 'command')   
        
        row = boxRender.row()
        row.scale_y = 1.5
        row.operator('wr360.render_view', icon='RENDER_RESULT')
        
        #or not scene.wr360Config.proj_name
        if not scene.wr360Config.out_dir or selected_obj is None or selected_obj.type not in ['MESH', 'EMPTY']:
            boxSetup.enabled = False
            boxRender.enabled = False
            boxCamera.enabled = False
            
        wr360_cam = scene.objects.get(scene.wr360Config.camera_name)
        if wr360_cam is None:
            boxRender.enabled = False
            boxCamera.enabled = False
            
def register():
    register_class(WR360_PT_Panel)

def unregister():
    unregister_class(WR360_PT_Panel)

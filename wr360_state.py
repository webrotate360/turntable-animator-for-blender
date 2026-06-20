'''
Copyright (C) WebRotate 360 LLC
support@webrotate360.com
''' 

import bpy
from bpy.types import Scene
import json
import os

class WR360_State():
    def switch_to_object_mode(self):
        if (bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT'):
            bpy.ops.object.mode_set(mode='OBJECT')
        
    def sync_scene_from_props(self, context):
        scene = context.scene
        
        v_circle_obj = scene.objects.get(scene.wr360Config.vert_track_name)
        if v_circle_obj:       
            org_distance = v_circle_obj['wr360CamSetupDistance']
            new_distance = scene.wr360Config.cam_distance
            new_scale = new_distance / org_distance
            v_circle_obj.scale = (new_scale, new_scale, new_scale)   

        wr360_cam = scene.objects.get(scene.wr360Config.camera_name)
        if wr360_cam:
            wr360_cam.data.lens = scene.wr360Config.cam_focal_length    

        scene.render.resolution_x = scene.wr360Config.x_resolution  
        scene.render.resolution_y = scene.wr360Config.y_resolution
        scene.render.use_border = scene.wr360Config.render_region
        scene.render.use_crop_to_border = scene.wr360Config.crop_region
    
    def sync_props_from_scene(self, scene):   
        wr360Config = scene.wr360Config
        wr360HotspotConfig = scene.wr360HotspotConfig
        
        active_obj = bpy.context.view_layer.objects.active
        if active_obj and 'wr360IsHotspot' in active_obj:
            if active_obj['wr360HotspotType'] == 'empty':
                hotspot_indicator = active_obj['wr360HotspotIndicator']
                # if hotspot_indicator:
                #    wr360HotspotConfig.hotspot_indicators = hotspot_indicator
            elif len(active_obj.vertex_groups) > 0:
                active_vertex_group_name = active_obj.vertex_groups[active_obj.vertex_groups.active_index].name
                vertex_group_obj_prop = 'wr360HotspotVertexGroup_' + active_vertex_group_name
                
                if wr360HotspotConfig.last_vertex_group_name != active_vertex_group_name:
                    wr360HotspotConfig.last_vertex_group_name = active_vertex_group_name
                    if vertex_group_obj_prop in active_obj:
                        json_str = active_obj.get(vertex_group_obj_prop);
                        json_prop = json.loads(active_obj.get(vertex_group_obj_prop))
                        wr360HotspotConfig.poly_popup_text = json_prop['text']
                    else:
                        wr360HotspotConfig.poly_popup_text = 'Demo popup text'
                else:
                    active_obj[vertex_group_obj_prop] = json.dumps({ 
                        'text': wr360HotspotConfig.poly_popup_text })   
        
        if wr360Config.x_resolution != scene.render.resolution_x:
            wr360Config.x_resolution = scene.render.resolution_x
            return
            
        if wr360Config.y_resolution != scene.render.resolution_y:    
            wr360Config.y_resolution = scene.render.resolution_y
            return
            
        if wr360Config.render_region != scene.render.use_border:
            wr360Config.render_region = scene.render.use_border
            return
            
        if wr360Config.crop_region != scene.render.use_crop_to_border:
            wr360Config.crop_region = scene.render.use_crop_to_border
            return
            
        wr360_cam = scene.objects.get(wr360Config.camera_name)
        if wr360_cam and wr360Config.cam_focal_length != wr360_cam.data.lens:
            wr360Config.cam_focal_length = wr360_cam.data.lens
            return
            
        if wr360Config.out_dir:
            wr360Config.proj_name = os.path.basename(os.path.normpath(wr360Config.out_dir))
        
    def first_frame_update(self, context):
        wr360Config = context.scene.wr360Config
        
        total_rows = wr360Config.vertical_row_up + wr360Config.vertical_row_down + 1
        total_frames = total_rows * wr360Config.frame_number;
        
        if total_frames < wr360Config.first_frame:
            wr360Config.first_frame = total_frames
        context.scene.frame_set(wr360Config.first_frame)
   
def register():
    Scene.wr360State = WR360_State()     

def unregister():
    del Scene.wr360State   
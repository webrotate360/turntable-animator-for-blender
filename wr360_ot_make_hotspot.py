'''
Copyright (C) WebRotate 360 LLC
support@webrotate360.com
'''

import os
import bpy
from bpy.utils import register_class, unregister_class

class WR360_OT_MakeHotspot(bpy.types.Operator):
    bl_idname = 'wr360.make_hotspot'
    bl_label = 'Make Hotspot'
    bl_description = 'Add or remove hotspot'
    
    type: bpy.props.StringProperty()
    
    def execute(self, context):
        wr360HotspotConfig = context.scene.wr360HotspotConfig
        active_obj = context.view_layer.objects.active
        isHotspot = False
        
        if 'wr360IsHotspot' in active_obj:
            isHotspot = active_obj['wr360IsHotspot']
            
        if isHotspot == True:
            active_obj['wr360IsHotspot'] = False
            active_obj['wr360HotspotName'] = None
            active_obj['wr360HotspotTxt'] = None
            active_obj['wr360HotspotType'] = None
            active_obj['wr360HotspotIndicator'] = None
        else:
            active_obj['wr360IsHotspot'] = True
            active_obj['wr360HotspotTxt'] = 'Demo popup text'
            active_obj['wr360HotspotType'] = self.type
            
            if self.type == 'poly':
                active_vertex_group_name = active_obj.vertex_groups[active_obj.vertex_groups.active_index].name
                active_obj['wr360HotspotIndicator'] = None
                active_obj['wr360HotspotName'] = active_vertex_group_name
                wr360HotspotConfig.last_vertex_group_name = active_vertex_group_name
            elif self.type == 'poly_mesh':
                active_obj['wr360HotspotIndicator'] = None
                active_obj['wr360HotspotName'] = active_obj.data.name   
            else:
                active_obj['wr360HotspotName'] = active_obj.name
                active_obj['wr360HotspotIndicator'] = wr360HotspotConfig.hotspot_indicators
            
        return {'FINISHED'}        
        
def register():
    register_class(WR360_OT_MakeHotspot)

def unregister():
    unregister_class(WR360_OT_MakeHotspot)        
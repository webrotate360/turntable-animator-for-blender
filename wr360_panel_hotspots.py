'''
Copyright (C) WebRotate 360 LLC
support@webrotate360.com
'''

import bpy
import os
from bpy.types import Panel
from bpy.utils import register_class, unregister_class
from bpy.types import UILayout, Operator

class WR360_PT_PanelHotspots(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WR360'
    bl_label = 'Hotspots'
     
    def draw(self, context):
        wr360Config = context.scene.wr360Config 
        wr360HotspotConfig = context.scene.wr360HotspotConfig
        active_obj = context.view_layer.objects.active
        
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        if active_obj: 
            isHotspot = False
            if 'wr360IsHotspot' in active_obj:
                isHotspot = active_obj['wr360IsHotspot']
                
            #col.enabled = isHotspot == True
            if isHotspot == True:
                hotspot_type = active_obj['wr360HotspotType']
                
                if hotspot_type == 'empty':
                    col = layout.row().column()
                    col.prop(active_obj, '["wr360HotspotName"]', text='Name')
                    col.enabled = False
                    col = layout.row().column()
                    col.prop(active_obj, '["wr360HotspotTxt"]', text='Popup Text')
                    col = col.template_icon_view(wr360HotspotConfig, 'hotspot_indicators', show_labels=False, scale=1.5, scale_popup=1.5)
                    icon_name, ext = os.path.splitext(wr360HotspotConfig.hotspot_indicators)
                    col = layout.row().column()
                    col.label(text='Indicator name: {}'.format(icon_name + '.svg'))
                elif hotspot_type == 'poly_mesh':
                    col = layout.row().column()
                    col.prop(active_obj, '["wr360HotspotName"]', text='Name')
                    col.enabled = False
                    col = layout.row().column()
                    col.prop(wr360HotspotConfig, 'poly_popup_text')
                    col.prop(wr360HotspotConfig, 'poly_backcolor_inactive')
                    col.prop(wr360HotspotConfig, 'poly_backcolor_active')
                    col.prop(wr360HotspotConfig, 'projection_type')
                else:
                    col = layout.row().column()
                    col.prop(wr360HotspotConfig, 'last_vertex_group_name', text='Name')
                    col.enabled = False
                    col = layout.row().column()
                    col.prop(wr360HotspotConfig, 'poly_popup_text')
                    col.prop(wr360HotspotConfig, 'poly_backcolor_inactive')
                    col.prop(wr360HotspotConfig, 'poly_backcolor_active')
                    col.prop(wr360HotspotConfig, 'projection_type')
                    
                col = layout.row().column()
                col.prop(wr360HotspotConfig, 'indicator_effect')   
                col = layout.row().column()
                col.prop(wr360HotspotConfig, 'indicator_effect_speed')   
                if wr360HotspotConfig.indicator_effect in ['none', 'scaleUp']:
                    col.enabled = False
                col = layout.row().column()
                col.prop(wr360HotspotConfig, 'indicator_effect_stop')   
                if wr360HotspotConfig.indicator_effect in ['none', 'scaleUp']:
                    col.enabled = False
                   
            if isHotspot == False:  
                col = layout.row().column()
                col.operator('wr360.make_hotspot', text='Hotspot From Empty').type = 'empty'
                if wr360Config.active_object is None or active_obj is None or active_obj.type not in ['EMPTY'] or active_obj == wr360Config.active_object:
                    col.enabled = False
                
                col = layout.row().column()
                col.operator('wr360.make_hotspot', text='Hotspot From Vertex Group').type = 'poly'
                if wr360Config.active_object is None or active_obj is None or active_obj.type not in ['MESH'] or len(active_obj.vertex_groups) == 0:
                    col.enabled = False
                    
                col = layout.row().column()
                col.operator('wr360.make_hotspot', text='Hotspot From Mesh').type = 'poly_mesh'
                if wr360Config.active_object is None or active_obj is None or active_obj.type not in ['MESH']:
                    col.enabled = False    
            else:
                col = layout.row().column()
                col.operator('wr360.make_hotspot', text='Remove Hotspot')

def register():
    register_class(WR360_PT_PanelHotspots)

def unregister():
    unregister_class(WR360_PT_PanelHotspots)

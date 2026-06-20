'''
Copyright (C) WebRotate 360 LLC
support@webrotate360.com
'''

import bpy
from bpy.types import Scene
import os
from bpy.utils import register_class, unregister_class
 
wr360_hotspot_icon_pcoll = None
     
def wr360_get_indicator_previews():
    global wr360_hotspot_icon_pcoll
    
    if wr360_hotspot_icon_pcoll is None:
        wr360_hotspot_icon_pcoll = bpy.utils.previews.new()
    path = os.path.join(os.path.dirname(__file__), 'icons')
    items = []
    
    for i, image in enumerate(os.listdir(path)):
        filepath = os.path.join(path, image)
        icon = wr360_hotspot_icon_pcoll.load(filepath, filepath, 'IMAGE')
        icon_name, ext = os.path.splitext(image)
        items.append((image, image, icon_name + '.svg', icon.icon_id, i))
  
    return items

def wr360_hotspot_indicator_update(self, context):
    active_obj = context.view_layer.objects.active
    if 'wr360HotspotIndicator' in active_obj:
        active_obj['wr360HotspotIndicator'] = self.hotspot_indicators;
        
class WR360_Settings_Hotspot(bpy.types.PropertyGroup):
    poly_popup_text: bpy.props.StringProperty(
        default='Demo popup text',
        name='Popup Text')   
        
    last_vertex_group_name: bpy.props.StringProperty(
        name='Last vertext group name')  
        
    hotspot_indicators: bpy.props.EnumProperty(
        name='Indicator',
        update=wr360_hotspot_indicator_update,
        items=wr360_get_indicator_previews())
        
    indicator_effect: bpy.props.EnumProperty(
        name='Animation',
        default='scaleUp',
        items=[
            ('none', 'No animation', '', 1),
            ('scaleUp', 'Scale up when visible', '', 2),
            ('pulseSimple', 'Simple pulse', '', 3),
            ('pulseOuter', 'Outer pulse', '', 4),
            ('pulseDoubleOuter', 'Double outer pulse', '', 5),
            ('pulseRipple', 'Ripple pulse', '', 6),
            ('pulseRinged', 'Ringed pulse', '', 7),
            ('spin', 'Spin', '', 8),
            ('flash', 'Flash', '', 9)])      

    indicator_effect_speed : bpy.props.IntProperty(
        name='Animation Speed',
        min=0, 
        max=100000, 
        default=2000)          
        
    indicator_effect_stop : bpy.props.BoolProperty(
        name='Stop on Activation',
        description='Stop animation on hotspot activation',
        default=True)     
        
    poly_backcolor_inactive: bpy.props.FloatVectorProperty(
        name='Inactive Color',
        subtype='COLOR',
        description='Background color when inactive',
        default=(1.0,1.0,1.0,1.0),
        size=4)
        
    poly_backcolor_active: bpy.props.FloatVectorProperty(
        name='Active Color',
        subtype='COLOR',
        description='Background color when activated',
        default=(1.0,1.0,1.0,1.0),
        size=4)   
        
    projection_type: bpy.props.EnumProperty(
        name='Projection Type',
        default='gift_wrap',
        description='Method of mapping a 3D hotspot to 2D images',
        items=[
            ('quad_mesh', 'Consecutive quads', '', 1),
            ('gift_wrap', 'Gift wrap', '', 2),
            ('flat_poly', '2D polygon', '', 3)])        
        
def register():
    register_class(WR360_Settings_Hotspot)
    Scene.wr360HotspotConfig = bpy.props.PointerProperty(type=WR360_Settings_Hotspot)      

def unregister():
    unregister_class(WR360_Settings_Hotspot)
    del Scene.wr360HotspotConfig
    if wr360_hotspot_icon_pcoll is not None:
        bpy.utils.previews.remove(wr360_hotspot_icon_pcoll)
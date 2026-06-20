'''
Copyright (C) WebRotate 360 LLC
support@webrotate360.com
'''

import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Scene
import bpy.utils.previews
import os
    
def wr360_props_update(self, context):
    context.scene.wr360State.sync_scene_from_props(context)
    
def wr360_first_frame_update(self, context):
    context.scene.wr360State.first_frame_update(context)           
            
class WR360_Settings(bpy.types.PropertyGroup):
    camera_name : bpy.props.StringProperty(
        default='WebRotate 360 Camera') 
    
    vert_track_name : bpy.props.StringProperty(
        default='WebRotate 360 Track')
        
    out_dir : bpy.props.StringProperty(
        name='Project Folder',
        description='WebRotate 360 for Blender project location',
        maxlen=1024,
        subtype='DIR_PATH')    
        
    proj_name : bpy.props.StringProperty(
        name='Project Name',
        description='Name of WebRotate 360 project',
        default='',
        maxlen=1024)     
        
    active_object : bpy.props.PointerProperty(
        name='Selected Object',
        description='Select object for animation and render',
        type=bpy.types.Object)
    
    vertical_angle_step : bpy.props.FloatProperty(
        name='Vertical Step',
        description='Vertical camera step in degrees',     
        min=0, 
        max=6.28319, 
        default=0,
        subtype='ANGLE')                
        
    vertical_row_up : bpy.props.IntProperty(
        name='Rows Up',
        description='Number of rows to move camera up',     
        min=0, 
        max=100, 
        default=0)        
        
    vertical_row_down : bpy.props.IntProperty(
        name='Rows Down',
        description='Number of rows to move camera down',     
        min=0, 
        max=100, 
        default=0)      

    frame_number : bpy.props.IntProperty(
        name='Frames Per Row',
        description='Number of frames (images) to render in a single row',     
        min=1, 
        max=1000, 
        default=40)     
        
    cam_distance : bpy.props.FloatProperty(
        name='Camera Distance',
        description='Camera distance',     
        min=1, 
        max=1000,
        default=0,
        subtype='DISTANCE',
        update=wr360_props_update)    
        
    cam_focal_length : bpy.props.FloatProperty(
        name='Focal Length',
        description='Camera focal length in mm',     
        min=1, 
        max=1000,
        default=75,
        subtype='DISTANCE_CAMERA',
        update=wr360_props_update)        
        
    x_resolution : bpy.props.IntProperty(
        name='Resolution X',
        description='Number of horizontal pixels in the rendered image',     
        min=4, 
        max=100000, 
        default=1920,
        update=wr360_props_update)          
        
    y_resolution : bpy.props.IntProperty(
        name='Y',
        description='Number of vertical pixels in the rendered image',     
        min=4, 
        max=100000, 
        default=1080,
        update=wr360_props_update)          
        
    render_region : bpy.props.BoolProperty(
        name='Render Region',
        description='Render user-defined region within the frame size',
        default=False,
        update=wr360_props_update)
        
    crop_region : bpy.props.BoolProperty(
        name='Crop to Render Region',
        description='Crop the rendered frame to the defined Render Region',
        default=False,
        update=wr360_props_update)    
        
    fast_render : bpy.props.BoolProperty(
        name='Use Fast Render',
        description='Use fast raw render for quick previews',
        default=True)     

    horiz_dir_clockwise : bpy.props.BoolProperty(
        name='Frames Spin Clockwise',
        description='Frame animation is clockwise relative to camera view',
        default=True)       
        
    flip_vert_input : bpy.props.BoolProperty(
        name='Flip Vertical Input',
        description='Flip the direction of vertical input from mouse or touch-screen',
        default=True)     

    skip_render : bpy.props.BoolProperty(
        name='Skip Re-render on Publish',
        description='Do not re-render images and just publish with updated settings',
        default=False)              
        
    viewer_skin : bpy.props.EnumProperty(
        name='Skin',
        default='basic',
        description='Skin of the viewer toolbar',
        items=[
            ('basic', 'basic', 'Basic skin', 0),    
            ('thin', 'thin', 'Thin skin', 1),    
            ('round', 'round', 'Round skin', 2),    
            ('empty', 'empty', 'Empty skin', 3),
            ('retina', 'retina', 'Retina skin', 4),
            ('zoom_light', 'zoom_light', 'Zoom Light skin', 5),
            ('zoom_dark', 'zoom_dark', 'Zoom Dark skin', 6)])

    viewer_background: bpy.props.FloatVectorProperty(
        name='Background',
        subtype='COLOR',
        description='Use this color to fill viewer background',
        default=(1.0,1.0,1.0,1.0),
        size=4)            
    
    first_frame : bpy.props.IntProperty(
        name='First Frame',
        description='First image to load when viewer starts',
        min=1, 
        default=1,
        update=wr360_first_frame_update)
        
    image_quality : bpy.props.IntProperty(
        name='Image Quality',
        min=0, 
        max=100,
        subtype='PERCENTAGE', 
        default=94)   
        
    image_format : bpy.props.EnumProperty(
        items=(
            ('jpg', 'JPG', ''),
            ('png', 'PNG', ''),),
        name='Image Format',
        default='jpg',
        description='Render image format')
        
    command : bpy.props.EnumProperty(
        name='Target',
        default='publish_project_launch',
        description='Select command to execute',
        items=[
            ('no_publish', 'Do not publish and just render images', '', 4),
            ('publish_project_launch', 'Publish project and open in SpotEditor', '', 3),    
            ('publish_project', 'Publish project', '', 2),    
            #('publish_view_launch', 'Publish view and open in QuickView', '', 1),
            ('publish_view', 'Publish view', '', 0)])
        
def register():
    register_class(WR360_Settings)
    Scene.wr360Config = bpy.props.PointerProperty(type=WR360_Settings)

def unregister():
    unregister_class(WR360_Settings)
    del Scene.wr360Config 
   
    
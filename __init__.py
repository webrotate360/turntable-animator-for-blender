'''
Copyright (C) WebRotate 360 LLC
support@webrotate360.com
'''

# TODO: disable controls until render is finished.
# TODO: for PNG apply defaults or add selection for RGBA
# TODO: macOS use os.popen
# TODO: macOS creates sub folder on macOS
# TODO: macOS doesn't save viewer background color
# TODO: selected viewer skin type is not saved

bl_info = {
    'name': 'WebRotate 360 Turntable Animator',
    'author': 'WebRotate 360 LLC',
    'version': (1, 2),
    'blender': (2, 80, 0),
    'location': 'Properties > Scene > WebRotate 360',
    'description': 'Create highly interactive 360 and multi-row 3D product views for online and offline publishing. This plugin adds several tools to your Blender panels to help creating turntable animations with hotspots and interactive polygonal areas in couple of clicks. For more advanced capabilities, use our advanced desktop publishing software, free CMS and E-commerce plugins, viewer APIs, a desktop viewer for offline use, as well as an optional CDN hosting dashboard for sharing and integrating your published 360 spins online with analytics.',
    'warning': '',
    'doc_url': '',
    'category': 'Render',
    'wiki_url': 'https://www.webrotate360.com/products/cms-and-e-commerce-plugins/plugin-for-blender.aspx'
}

import sys
import importlib
import bpy
import platform
from bpy.app.handlers import persistent

is_mac = platform.system() == "Darwin"

module_names = [
    'wr360_state', 
    'wr360_publisher',
    'wr360_settings_mac' if is_mac else 'wr360_settings',
    'wr360_settings_hotspot', 
    'wr360_ot_animate', 
    'wr360_ot_render_view',
    'wr360_panel', 
    'wr360_panel_hotspots', 
    'wr360_ot_make_hotspot']
    
module_full_names = [ f"{__name__}.{module}" for module in module_names ]
        
for module in module_full_names:
    if module in sys.modules:
        importlib.reload(sys.modules[module])
    else:
        locals()[module] = importlib.import_module(module)
        setattr(locals()[module], 'module_names', module_full_names)
        
@persistent
def wr360PersistentUpdate(scene):    
    scene.wr360State.sync_props_from_scene(scene)
    
def register():    
    for module in module_full_names:
        if module in sys.modules:
            if hasattr(sys.modules[module], 'register'):
                sys.modules[module].register()
                
    pre_handlers = bpy.app.handlers.depsgraph_update_pre
    [pre_handlers.remove(h) for h in pre_handlers if h.__name__ == 'wr360PersistentUpdate']
    pre_handlers.append(wr360PersistentUpdate) 
   
def unregister():
    for module in module_full_names:
        if module in sys.modules:
            if hasattr(sys.modules[module], 'unregister'):
                sys.modules[module].unregister()
'''
Copyright (C) WebRotate 360 LLC
support@webrotate360.com
'''

import bpy
import math
import bpy_extras
from bpy.utils import register_class, unregister_class
 
class WR360_OT_To_Setup_Frame(bpy.types.Operator):
    bl_idname = 'wr360.to_setup_frame'
    bl_label = 'Return to setup frame'
    bl_description = 'Jump to the frame that was used to setup the current animation'

    @classmethod
    def poll(cls, context):
        wr360_cam = context.scene.objects.get(context.scene.wr360Config.camera_name)
        return wr360_cam is not None
        
    def execute(self, context):
        wr360Config = context.scene.wr360Config
        context.scene.wr360State.switch_to_object_mode()
        
        wr360_cam = context.scene.objects.get(wr360Config.camera_name)
        
        for area in bpy.context.window.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].region_3d.view_perspective = 'CAMERA'
                
        wr360Config = context.scene.wr360Config
        if wr360Config.vertical_row_down > 0:
            setup_frame = wr360Config.vertical_row_down * wr360Config.frame_number + 1;
            context.scene.frame_set(setup_frame)
        else:
            context.scene.frame_set(1)
        return {'FINISHED'}
 
class WR360_OT_Animate(bpy.types.Operator):
    bl_idname = 'wr360.animate'
    bl_label = 'Setup animation'
   
    def group_collection(self, objects_to_group):
        collection_name = 'WR360'
        if collection_name in bpy.data.collections:
            collection = bpy.data.collections[collection_name]
        else:
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)
            
        for obj in objects_to_group:
            if isinstance(obj, bpy.types.Curve):
                obj = bpy.data.objects.new(obj.name, obj)
            if obj.users_collection:
                obj.users_collection[0].objects.unlink(obj)
                
            collection.objects.link(obj)
        
    def align_plane_to_point(self, obj, point):
        dir = point - obj.location
        return dir.to_track_quat('Y', 'X').to_euler()
    
    def execute(self, context):
        wr360Config = context.scene.wr360Config
        context.scene.wr360State.switch_to_object_mode()
        
        selected_obj = wr360Config.active_object 
        bpy.ops.object.select_all(action = 'DESELECT') 
     
        # Delete previous states
        selected_obj.animation_data_clear()
        
        v_circle_obj = context.scene.objects.get(context.scene.wr360Config.vert_track_name)
        if v_circle_obj:
            bpy.data.objects.remove(v_circle_obj, do_unlink=True)
            
        wr360_cam = context.scene.objects.get(context.scene.wr360Config.camera_name)
        if wr360_cam:
            bpy.data.objects.remove(wr360_cam, do_unlink=True)
            
        # Create dedicated animation camera and make current
        wr360_cam_data = bpy.data.cameras.new(context.scene.wr360Config.camera_name)
        wr360_cam_data.lens = wr360Config.cam_focal_length
        wr360_cam = bpy.data.objects.new(context.scene.wr360Config.camera_name, wr360_cam_data)
        context.scene.collection.objects.link(wr360_cam)
        context.scene.camera = wr360_cam;
        
        # Set camera view to current users view
        for area in bpy.context.window.screen.areas:
            if area.type == 'VIEW_3D':
                wr360_cam.matrix_world = area.spaces[0].region_3d.view_matrix
                wr360_cam.matrix_world.invert()
                space_data = area.spaces[0]
                space_data.region_3d.view_perspective = 'CAMERA'
            
        # Create Track To constraint to obj center.    
        t_constr = wr360_cam.constraints.new(type='TRACK_TO')
        t_constr.target = selected_obj
        t_constr.track_axis = 'TRACK_NEGATIVE_Z'
        t_constr.up_axis = 'UP_Y'
        
        # Apply any existing transforms to selected object.
        context.view_layer.objects.active = selected_obj
        selected_obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        
        # Set to compatible rotation mode as this is how we animate.
        selected_obj.rotation_mode = 'XYZ'
       
        # Get distance from obj to camera
        dist = (selected_obj.location - wr360_cam.location).length
        
        # Draw tracking circle for vert camera spin with the distance being its radius.
        bpy.ops.curve.primitive_bezier_circle_add(
            location=selected_obj.location,
            radius=dist)

        # Turn circle vertically & horizontally to touch camera position 
        v_circle_obj = context.active_object
        v_circle_obj.name = context.scene.wr360Config.vert_track_name
        v_circle_obj.rotation_euler = self.align_plane_to_point(v_circle_obj, wr360_cam.location)
        v_circle_obj['wr360CamSetupDistance'] = dist
        wr360Config.cam_distance = dist
       
        # Parent cam to vertical circle track
        wr360_cam.select_set(True)
        v_circle_obj.select_set(True)
        context.view_layer.objects.active = v_circle_obj
        bpy.ops.object.parent_set(type='OBJECT')
        
        # Deselect all and make our main obj active
        bpy.ops.object.select_all(action = 'DESELECT')
        context.view_layer.objects.active = selected_obj
        
        # Save current rotation of the circle
        v_offset_curr = v_circle_obj.rotation_euler[1]
        v_camera_step = wr360Config.vertical_angle_step 
        
        # Depending on how circle track got aligned on X axes via align_plane_to_point, the direction of step may need flipping
        if v_circle_obj.rotation_euler[0] > 0:
            v_camera_step = -v_camera_step
        
        # If downward rows set, calc rotation of the circle to spin it down (with attached cam) to get to the first bottom row.
        if wr360Config.vertical_row_down > 0:
            v_offset_curr = v_offset_curr + (wr360Config.vertical_row_down * v_camera_step)
            
        # By default we animate vertical camera from top to bottom.
        # if wr360Config.vert_cam_starts_top:
        #    v_offset_curr = v_offset_curr - (wr360Config.vertical_row_down + wr360Config.vertical_row_up) * v_camera_step
        #    v_offset_curr = -v_offset_curr
            
        frame_pos = 1
        
        # Change rotation transform to gimbal so we can spin the vert circle track along its plane.
        orientation_save = context.scene.transform_orientation_slots[0].type;
        context.scene.transform_orientation_slots[0].type = 'GIMBAL' 

        total_rows = wr360Config.vertical_row_up + wr360Config.vertical_row_down + 1
        
        # For vertical cam animation when there's just one row.
        ascend_max_steps = wr360Config.frame_number / 2
        
        spin_dir = -1
        if not wr360Config.horiz_dir_clockwise:
            spin_dir = 1
              
        for row_num in range(0, total_rows): 
            for frame_num in range(0, wr360Config.frame_number): 
                context.scene.frame_set(frame_pos)
                
                # For vertical cam animation when there's just one row.
                # Needs a slow down easing at the bottom & top of the curve.
                if total_rows == 1:
                    if (frame_num < ascend_max_steps):
                        v_offset_curr -= v_camera_step
                    elif (frame_num < ascend_max_steps * 2):
                        v_offset_curr += v_camera_step
                
                v_circle_obj.rotation_euler[1] = v_offset_curr
                #print(frame_num * (math.pi / wr360Config.frame_number) * 2)
                selected_obj.rotation_euler[2] = spin_dir * frame_num * (math.pi / wr360Config.frame_number) * 2
                v_circle_obj.keyframe_insert(data_path='rotation_euler', index=-1)
                selected_obj.keyframe_insert(data_path='rotation_euler', index=-1)
                
                frame_pos += 1
                
            v_offset_curr -= v_camera_step
     
        if wr360Config.vertical_row_down > 0:
            setup_frame = wr360Config.vertical_row_down * wr360Config.frame_number + 1;
            context.scene.frame_set(setup_frame)
        else:
            context.scene.frame_set(1)

        bpy.data.scenes["Scene"].frame_start = 1
        bpy.data.scenes["Scene"].frame_end = frame_pos - 1
            
        # Restore original orientation before plugin run
        context.scene.transform_orientation_slots[0].type = orientation_save;
        
        self.group_collection([v_circle_obj, wr360_cam])
        
        return {'FINISHED'}
            
def register():
    register_class(WR360_OT_Animate)
    register_class(WR360_OT_To_Setup_Frame)

def unregister():
    unregister_class(WR360_OT_Animate)
    unregister_class(WR360_OT_To_Setup_Frame)

'''
Copyright (C) WebRotate 360 LLC
support@webrotate360.com
'''

import os
import shutil
import bpy
import bmesh
import time
import json
import math
import platform
from collections import defaultdict
import xml.etree.ElementTree as ET
from bpy.utils import register_class, unregister_class
import bpy_extras
from bpy.types import Scene
from mathutils import Vector
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from collections import deque

class WR360_Publisher():
    wr360Config = None
    wr360HotspotConfig = None
    wr360State = None
    project_dir = None
    proj_name = None
    templ_view_dir = None
    hotspots = []
    hotspots_positions = []
    ray_tracer_name = 'wr360RayTest'
        
    def init(self, context, folder_name):
        self.wr360Config = context.scene.wr360Config
        self.wr360State = context.scene.wr360State
        self.wr360HotspotConfig = context.scene.wr360HotspotConfig
        self.proj_name = os.path.basename(os.path.normpath(self.wr360Config.out_dir))
        self.project_dir = os.path.join(self.wr360Config.out_dir, folder_name)
        self.templ_view_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)) , 'assets', 'template')
        self.templ_proj_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)) , 'assets', 'project')
        
    def initRender(self, context, path):
        render_format = self.wr360Config.image_format.upper()
        if render_format == 'JPG':
            render_format = 'JPEG'
            context.scene.render.image_settings.quality = self.wr360Config.image_quality
        context.scene.render.image_settings.file_format = render_format
        context.scene.render.filepath = path
        
    def render(self, context, folder_name): 
        self.init(context, folder_name)
        self.initRender(context,os.path.join(self.project_dir, 'render'))
  
        if self.wr360Config.fast_render:
            bpy.ops.render.opengl(animation=True, write_still=True)
        else:
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True)
    
    def render_project(self, context, folder_name):        
        self.init(context, folder_name)
        self.initRender(context, os.path.join(self.project_dir, 'images', 'render'))
        self.create_proj(context)
        
        if self.wr360Config.fast_render:
            bpy.ops.render.opengl(animation=True, write_still=True)
            self.handle_project_complete(context.scene, None)
        else:
            if not 'handle_project_complete' in [hand.__name__ for hand in bpy.app.handlers.render_complete]:
                bpy.app.handlers.render_complete.append(self.handle_project_complete)
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True)
        
    def update_project(self, context, folder_name):   
        self.init(context, folder_name);
        self.create_proj(context)
        if 'launch' in self.wr360Config.command:
            self.launch_spoteditor()
        self.reset_animation_frame(context.scene)
        
    def handle_project_complete(self, scene, depthgraph):
        if 'launch' in self.wr360Config.command:
            self.launch_spoteditor()
        self.reset_animation_frame(scene)    
        
    def render_view(self, context, folder_name):        
        self.init(context, folder_name)
        self.initRender(context, os.path.join(self.project_dir, 'images', 'render'))
        self.create_view(context)
       
        if self.wr360Config.fast_render:
            bpy.ops.render.opengl(animation=True, write_still=True)
            self.handle_view_complete(context.scene, None)
        else:
            if not 'handle_view_complete' in [hand.__name__ for hand in bpy.app.handlers.render_complete]:
                bpy.app.handlers.render_complete.append(self.handle_view_complete)
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True)
    
    def update_view(self, context, folder_name):   
        self.init(context, folder_name)
        self.create_view(context)
        self.finalize_view()
        if 'launch' in self.wr360Config.command:
            self.launch_quick_view()
        self.reset_animation_frame(context.scene)
      
    def handle_view_complete(self, scene, depthgraph):
        self.finalize_view()
        if 'launch' in self.wr360Config.command:
            self.launch_quick_view()
        self.reset_animation_frame(scene)
        
    def getHexBackcolor(self):
        if self.wr360Config.viewer_background[3] == 0:
            return 'transparent'
        else:
            return '{:02x}{:02x}{:02x}'.format(
                int(self.wr360Config.viewer_background[0] * 255), 
                int(self.wr360Config.viewer_background[1] * 255),
                int(self.wr360Config.viewer_background[2] * 255))
        
    def create_view(self, context):  
        os.makedirs(self.project_dir, exist_ok=True)
        shutil.copytree(self.templ_view_dir, self.project_dir, dirs_exist_ok=True)
        self.create_view_xml(context, True);
        os.replace(os.path.join(self.project_dir, 'template.pxrtcont'), os.path.join(self.project_dir, self.proj_name + '.pxrtcont'))
       
        lic = ''
        lic_file = os.path.join(self.project_dir, 'license.lic')
        if os.path.isfile(lic_file):
            with open(lic_file, 'r') as f:
                lic = f.readline().strip()
            try:
                os.remove(lic_file)
            except OSError as e:
                print(f'Error deleting {lic_file}: {e.strerror}')                
    
        loc_obj = {
            'licenseCode': lic,
            'backgroundColor': self.getHexBackcolor()
        }

        with open(os.path.join(self.project_dir, self.proj_name + '.view'), 'w') as f:
            json.dump(loc_obj, f)
     
    def create_proj(self, context):  
        os.makedirs(self.project_dir, exist_ok=True)
        shutil.copytree(self.templ_proj_dir, self.project_dir, dirs_exist_ok=True)
        self.create_view_xml(context, False);
        
        proj_file_path = os.path.join(self.project_dir, self.proj_name + '.xml.wr360')
        temp_file_path = os.path.join(self.project_dir, 'template.xml.wr360')
        
        if os.path.exists(proj_file_path):
            os.replace(proj_file_path, temp_file_path)
            
        self.create_proj_xml(context);

        shutil.copy(temp_file_path, proj_file_path)
        #os.replace(temp_file_path, proj_file_path)
        
    def create_proj_xml(self, context):
        xml_path = os.path.join(self.project_dir, 'template.xml.wr360')
        xml_doc = ET.parse(xml_path)
        xml_root = xml_doc.getroot()
        
        xml_proj_name = xml_root.find('./projectName')
        xml_proj_name.text = self.proj_name
        xml_proj_conf = xml_root.find('./projectConfig') 
        xml_proj_conf.text = os.path.join(self.project_dir, self.proj_name + '.xml')
        xml_view_name = xml_root.find('./publishing/viewName')
        xml_view_name.text = self.proj_name   
        xml_skin_type = xml_root.find('./publishing/skinType')
        xml_skin_type.text = str(self.get_skin_type(self.wr360Config.viewer_skin))
        
        xml_back_color = xml_root.find('./publishing/viewerBackColor')
        
        rgba_bk_color = (
            int(self.wr360Config.viewer_background[0] * 255),
            int(self.wr360Config.viewer_background[1] * 255),
            int(self.wr360Config.viewer_background[2] * 255),
            int(self.wr360Config.viewer_background[3] * 255))
            
        argb_bk_color = (rgba_bk_color[3] << 24) | (rgba_bk_color[0] << 16) | (rgba_bk_color[1] << 8) | rgba_bk_color[2]
        
        xml_back_color.text = str(np.int32(np.int64(argb_bk_color)))
        xml_doc.write(xml_path)
    
    def create_view_xml(self, context, is_final_view):
        xml_path = os.path.join(self.project_dir, 'template.xml')
        first_image_idx = self.wr360Config.first_frame - 1
        file_extension = '.' + self.wr360Config.image_format
        row_num = self.wr360Config.vertical_row_up + self.wr360Config.vertical_row_down + 1
        
        xml_doc = ET.parse(xml_path)
        xml_root = xml_doc.getroot()
        
        xml_preloader = xml_root.find('./settings/preloader')
        preloader_url = 'images/render' + str(first_image_idx + 1).zfill(4) + file_extension
        if is_final_view:
            preloader_url += '?t=' + str(int(time.time()))
        xml_preloader.attrib['image'] = preloader_url
        
        xml_ui = xml_root.find('./settings/userInterface')
        xml_ui.attrib['skin'] = self.wr360Config.viewer_skin
        xml_ui.attrib['fullScreenBackColor'] = '#' +  self.getHexBackcolor()
        
        xml_rotation = xml_root.find('./settings/rotation')
        xml_rotation.attrib['firstImage'] = str(first_image_idx)
        xml_rotation.attrib['flipVerticalInput'] = str(self.wr360Config.flip_vert_input).lower()
        
        xml_hotspots = xml_root.find('./hotspots')
        
        self.capture_hotspots(context)
     
        for hotspot in self.hotspots:
            obj = hotspot['obj']
            hotspot_type = obj['wr360HotspotType']
            hotspot_popup_text = obj['wr360HotspotTxt']
            xml_hotspot = ET.SubElement(xml_hotspots, 'hotspot')
            xml_hotspot.attrib['id'] = hotspot['name']
            xml_hotspot.attrib['renderMode'] = '0'
            xml_hotspot.attrib['activateOnClick'] = 'true'
            xml_hotspot.attrib['deactivateOnClick'] = 'true'
            
            if hotspot_type == 'empty':    
                icon_name, ext = os.path.splitext(self.wr360HotspotConfig.hotspot_indicators) #obj['wr360HotspotIndicator'])
                xml_hotspot.attrib['indicatorImage'] = icon_name + '.svg'
            else:    
                inactive_color = '#{:02x}{:02x}{:02x}'.format(
                    int(self.wr360HotspotConfig.poly_backcolor_inactive[0] * 255), 
                    int(self.wr360HotspotConfig.poly_backcolor_inactive[1] * 255),
                    int(self.wr360HotspotConfig.poly_backcolor_inactive[2] * 255))
                inactive_color_opacity = self.wr360HotspotConfig.poly_backcolor_inactive[3]
                
                active_color = '#{:02x}{:02x}{:02x}'.format(
                    int(self.wr360HotspotConfig.poly_backcolor_active[0] * 255), 
                    int(self.wr360HotspotConfig.poly_backcolor_active[1] * 255),
                    int(self.wr360HotspotConfig.poly_backcolor_active[2] * 255))
                active_color_opacity = self.wr360HotspotConfig.poly_backcolor_active[3]
               
                if hotspot_type == 'poly_mesh':
                    xml_hotspot.attrib['clipStyle'] = '{},{},{},{}'.format(
                        inactive_color, inactive_color_opacity, active_color, active_color_opacity)             
                else:
                    vertex_group_obj_prop = 'wr360HotspotVertexGroup_' + hotspot['name']
                    if vertex_group_obj_prop in obj:
                        json_prop = json.loads(obj[vertex_group_obj_prop])
                        hotspot_popup_text = json_prop['text']
                        xml_hotspot.attrib['clipStyle'] = '{},{},{},{}'.format(
                            inactive_color, inactive_color_opacity, active_color, active_color_opacity)  
            
            if  self.wr360HotspotConfig.indicator_effect != 'none':
                if  self.wr360HotspotConfig.indicator_effect != 'scaleUp':
                    effects = f"{self.wr360HotspotConfig.indicator_effect},{self.wr360HotspotConfig.indicator_effect_speed}"
                    if self.wr360HotspotConfig.indicator_effect_stop:
                        effects = effects + ',1';
                    xml_hotspot.attrib['effects'] = effects
                else:
                    xml_hotspot.attrib['effects'] = 'scaleUp'
                        
            spot_info = ET.SubElement(xml_hotspot, 'spotinfo')
            spot_info.attrib['txt'] = hotspot_popup_text
            spot_info.attrib['css'] = 'font-size:13px;color:#333333;text-align:center;width:180px;padding:15px 15px 17px 15px;border:1px solid #D9D9D9;border-radius:4px;background-color:rgba(255,255,255,1);' 
            
        xml_images = xml_root.find('./images')
        xml_images.attrib['rows'] = str(row_num)
        
        total_images = row_num * self.wr360Config.frame_number
        
        for image_index in range(0, total_images): 
            xml_image = ET.SubElement(xml_images, 'image')
            image_url = 'images/render' + str(image_index + 1).zfill(4) + file_extension
            if is_final_view:
                image_url += '?t=' + str(int(time.time()))
            
            xml_image.attrib['src'] = image_url
            if len(self.hotspots_positions) > 0:
                for h_pos in self.hotspots_positions[image_index]:
                    group_xy = h_pos['group_xy'];
                    
                    if h_pos['type'] == 'empty' and len(group_xy) == 1:
                        xml_hotspot = ET.SubElement(xml_image, 'hotspot')
                        xml_hotspot.attrib['source'] = h_pos['name']               
                        xml_hotspot.attrib['offsetX'] = '{:.1f}'.format(float(group_xy[0]['x']))
                        xml_hotspot.attrib['offsetY'] = '{:.1f}'.format(float(group_xy[0]['y']))
                    
                    elif len(group_xy) > 1:
                        xml_hotspot = ET.SubElement(xml_image, 'hotspot')
                        xml_hotspot.attrib['source'] = h_pos['name'] 
                        clip = h_pos['clip'] 
                        
                        xml_hotspot.attrib['clip'] = '{:.1f},{:.1f},{:.1f},{:.1f}'.format(
                            float(clip['left']),
                            float(clip['top']),
                            float(clip['width']),
                            float(clip['height']))
                            
                        for xy in group_xy:
                            xml_point = ET.SubElement(xml_hotspot, 'point')
                            x = float(xy['x'])
                            y = float(xy['y'])
                            if is_final_view:
                                x = x / clip['width'] * 100
                                y = y / clip['height'] * 100
                            xml_point.attrib['x'] = '{:.1f}'.format(x) 
                            xml_point.attrib['y'] = '{:.1f}'.format(y) 
            
        xml_doc.write(xml_path)
        
        os.replace(xml_path, os.path.join(self.project_dir, self.proj_name + '.xml'))
        
    def finalize_view(self):      
        first_image_idx = 0
        file_extension = '.' + self.wr360Config.image_format
        
        first_image_path = os.path.join(self.project_dir, 'images', 'render' + str(first_image_idx + 1).zfill(4) + file_extension)
        cover_image_path = os.path.join(self.project_dir, 'cover' + file_extension)
        shutil.copy(first_image_path, cover_image_path)
        
    def launch_quick_view(self):  
        bpy.ops.wm.url_open(url=os.path.join(self.project_dir, self.proj_name + '.view'))
        
    def launch_spoteditor(self):
        proj_file = os.path.join(self.project_dir, self.wr360Config.proj_name + '.xml.wr360')
        if platform.system() == 'Darwin':
            os.popen('open ' + proj_file) 
        else:
            bpy.ops.wm.url_open(url=proj_file)
        
    def reset_animation_frame(self, scene):   
        if self.wr360Config.vertical_row_down > 0:
            original_cam_frame = self.wr360Config.vertical_row_down * self.wr360Config.frame_number + 1;
            scene.frame_set(original_cam_frame)
        else:
            scene.frame_set(1)    
    
    def is_empty_coord_visible(self, depth_graph, coord, hotspot_name, scene, camera):
        direction = camera.location - coord
        result = scene.ray_cast(depth_graph, coord + direction * 0.0001, direction)
        intersect = result[0]
        hit = result[1]
        intersect_obj = result[4] 
        
        if intersect == False or intersect_obj.name == hotspot_name:
            return True
        return False	
        
    def is_mesh_coord_visible(self, depth_graph, coord, scene, camera):
        trace_cube =  bpy.data.objects[self.ray_tracer_name] 
        trace_cube.location = coord
        depth_graph = bpy.context.evaluated_depsgraph_get()
        result= scene.ray_cast(depth_graph, camera.location, (coord - camera.location).normalized())
        
        intersect = result[0]
        hit_coord = result[1]
        intersect_obj = result[4] 
    
        hit_distance = (coord - hit_coord).length
        visible = intersect and self.ray_tracer_name in intersect_obj.name
       
        return visible	
        	
    def get_hotspot_coords(self, hotspot, scene, cam):
        coords = []
        obj = hotspot['obj']
        hotspot_type = obj['wr360HotspotType']    
        
        if hotspot_type == 'poly':
            group_index = hotspot['group_index']
            for vertex in obj.data.vertices:
                if group_index in [group.group for group in vertex.groups]:
                    coords.append({ 'v': obj.matrix_world @ vertex.co, 'face': 0 })
        elif hotspot_type == 'poly_mesh':
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            for face in bm.faces:
                for vertex in face.verts:
                    coords.append({ 'v': obj.matrix_world @ vertex.co, 'face': face.index })
        else:
            coords.append({ 'v': obj.matrix_world.translation, 'face': 0 })
        
        return coords
        
    def get_poly_bounds(self, group_xy):
        min_x = min(coord['x'] for coord in group_xy)
        max_x = max(coord['x'] for coord in group_xy)
        min_y = min(coord['y'] for coord in group_xy)
        max_y = max(coord['y'] for coord in group_xy)
    
        return { 'left': min_x, 'top': min_y, 'width': max_x - min_x, 'height': max_y - min_y }
    
    def get_mesh_poly_merge_xy(self, group_xy, bounds_rect):
        # Build a dictionary with the face index as the key and a list of coordinates as the value.
        face_dict = defaultdict(list)
        for coord in group_xy:
            face_dict[coord['face']].append(coord)

        # Create a dictionary with visible groups only.
        visible_face_dict = {}
        for face, coords in face_dict.items():
            if all(coord['visible'] for coord in coords):
                visible_face_dict[face] = coords

        # Create a sorted list of faces
        sorted_faces = [visible_face_dict[face] for face in sorted(visible_face_dict)]
        
        # Convert each face to a polygon
        polygons = [[(coord['x'], coord['y']) for coord in face] for face in sorted_faces]
    
        def distance(vertex1, vertex2):
            x1, y1 = vertex1
            x2, y2 = vertex2
            return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
       
        def line_intersection(line1, line2):
            xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
            ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

            def det(a, b):
                return a[0] * b[1] - a[1] * b[0]

            div = det(xdiff, ydiff)
            if div == 0:
               return False

            d = (det(*line1), det(*line2))
            x = det(d, xdiff) / div
            y = det(d, ydiff) / div
            min_x, max_x = sorted([line1[0][0], line1[1][0]])
            min_y, max_y = sorted([line1[0][1], line1[1][1]])
            if min_x <= x <= max_x and min_y <= y <= max_y:
                return True
            return False

        def arrange_by_distance(non_shared_poly1, adjacent_index_in_non_shared):
            remaining_vertices = non_shared_poly1[:adjacent_index_in_non_shared] + non_shared_poly1[adjacent_index_in_non_shared + 1:]
            remaining_vertices.sort(key=lambda vertex: distance(vertex, non_shared_poly1[adjacent_index_in_non_shared]))
            arranged_poly1 = non_shared_poly1[adjacent_index_in_non_shared:adjacent_index_in_non_shared+1] + remaining_vertices
            return arranged_poly1
    
        def merge_polygons(poly1, poly2):
            shared_vertices = [vertex for vertex in poly1 if vertex in poly2]
            shared_vertices_reduced = shared_vertices
            num_shared = len(shared_vertices)
            if num_shared < 2 or num_shared > 3:
                return poly1
    
            if len(shared_vertices) == 3:
                # Compute all pairwise distances and store them with the corresponding pairs
                distances = [(vertex1, vertex2, distance(vertex1, vertex2)) for vertex1 in shared_vertices for vertex2 in shared_vertices if vertex1 != vertex2]
                # Sort the list of distances
                distances.sort(key=lambda x: x[2])
                # The vertices corresponding to the maximum distance are the ones we are looking for
                shared_vertices_reduced = [distances[-1][0], distances[-1][1]]

            # Identify the non-shared vertices in each polygon
            non_shared_poly1 = [vertex for vertex in poly1 if vertex not in shared_vertices]
            non_shared_poly2 = [vertex for vertex in poly2 if vertex not in shared_vertices]
            closest_vertex_poly2 = non_shared_poly2[0]
            distant_vertex_poly2 = None

            if len(non_shared_poly2) == 2:
                distant_vertex_poly2 = non_shared_poly2[1]
                line1 = [shared_vertices[0], non_shared_poly2[0]]
                line2 = [shared_vertices[1], non_shared_poly2[1]]
                if line_intersection(line1, line2):
                    closest_vertex_poly2 = non_shared_poly2[1]
                    distant_vertex_poly2 = non_shared_poly2[0]
          
            # Identify the index in poly1 of the vertex adjacent to shared_vertices_reduced[1]
            adjacent_index_in_poly1 = (poly1.index(shared_vertices_reduced[1]) - 1) % len(poly1)
          
            # Identify the vertex in poly1 at this index
            adjacent_vertex_in_poly1 = poly1[adjacent_index_in_poly1]
            if adjacent_vertex_in_poly1 not in non_shared_poly1:
                adjacent_index_in_poly1 = (poly1.index(shared_vertices_reduced[1]) + 1) % len(poly1)
                adjacent_vertex_in_poly1 = poly1[adjacent_index_in_poly1]
          
            # Identify the index of this vertex in non_shared_poly1
            adjacent_index_in_non_shared = non_shared_poly1.index(adjacent_vertex_in_poly1)

            # Rearrange non_shared_poly1 to start from this index
            non_shared_poly1 = arrange_by_distance(non_shared_poly1, adjacent_index_in_non_shared)
          
            if distant_vertex_poly2 is None:
                return [shared_vertices_reduced[0], closest_vertex_poly2] + [shared_vertices_reduced[1]] + non_shared_poly1
            
            # Return the ordered list of vertices
            return [shared_vertices_reduced[0], closest_vertex_poly2, distant_vertex_poly2] + [shared_vertices_reduced[1]] + non_shared_poly1

        def merge_all_polygons(polygons):
            if len(polygons) <= 1:
                # If there is one or zero polygons, nothing to merge
                return polygons
            
            # Attempt to merge the first two polygons
            merged = merge_polygons(polygons[0], polygons[1])

            if merged is not None:
                # If they were successfully merged, replace them with the result
                return merge_all_polygons([merged] + polygons[2:])
            else:
                # If they couldn't be merged, try again without the first polygon
                return merge_all_polygons(polygons[1:] + [polygons[0]])

        # Then replace the while loop with this:
        polygons = merge_all_polygons(polygons)
              
        if polygons and polygons[0] is not None:
            return [{
                'x': point[0] - bounds_rect['left'], 
                'y': point[1] - bounds_rect['top'] 
            } for point in polygons[0]]
         
        return []
        
    def get_vgroup_poly_xy(self, group_xy, bounds_rect):
        # Sort group_xy based on their x-values
        sorted_coords = sorted(group_xy, key=lambda coord: coord['x'])
        
        # Find the coordinate(s) with the lowest y-value(s)
        min_y = min(coord['y'] for coord in sorted_coords)
        starting_coords = [coord for coord in sorted_coords if coord['y'] == min_y]
        
        # Choose the leftmost group_xy as the starting point
        start_coord = min(starting_coords, key=lambda coord: coord['x'])
        
        # Calculate angles relative to the starting point
        angles = []
        for coord in group_xy:
            if coord != start_coord:
                angle = math.atan2(coord['y'] - start_coord['y'], coord['x'] - start_coord['x'])
                angles.append((angle, coord))
        
        # Sort the remaining coordinates based on their angle relative to the starting point
        sorted_coords = [start_coord] + [coord for angle, coord in sorted(angles)]
        
        # Make coordinates relative to the bounds
        for coord in sorted_coords:
            coord['x'] -= bounds_rect['left']
            coord['y'] -= bounds_rect['top']
        
        return sorted_coords

    def get_mesh_poly_hull_xy(self, group_xy, bounds_rect):
        # Construct the convex hull of a set of points.
        
        # Build a list with all coordinates
        all_coords = [(coord['x'], coord['y']) for coord in group_xy if coord['visible']]

        # Return early if no coordinates
        if len(all_coords) == 0:
            return []

        # Function to calculate angle between two vectors
        def angle(v1, v2):
            dot_product = v1[0] * v2[0] + v1[1] * v2[1]
            norm_product = math.sqrt(v1[0] ** 2 + v1[1] ** 2) * math.sqrt(v2[0] ** 2 + v2[1] ** 2)
            if norm_product == 0:  # Check if norm product is zero
                return 0
            adjusted_dot_product = dot_product / norm_product
            adjusted_dot_product = max(-1, min(adjusted_dot_product, 1))  # Ensure value is within valid range for acos
            return math.acos(adjusted_dot_product)

        # Gift wrapping (Jarvis March) algorithm implementation
        start_point = max(all_coords, key=lambda point: point[0])  # Start from the rightmost point
        polygon = [start_point]  # Initialize polygon with start point

        prev_point = start_point
        current_point = None
        vector1 = (0, 1)

        while current_point != start_point:
            smallest_angle = float('inf')
            next_point = None
            for point in all_coords:
                if point == prev_point:
                    continue
                vector2 = (point[0] - prev_point[0], point[1] - prev_point[1])
                current_angle = angle(vector1, vector2)
                if current_angle < smallest_angle:
                    smallest_angle = current_angle
                    next_point = point
            polygon.append(next_point)
            vector1 = (next_point[0] - prev_point[0], next_point[1] - prev_point[1])
            prev_point = next_point
            current_point = next_point

        # Adjust points according to the bounding rectangle and return
        return [{'x': point[0] - bounds_rect['left'], 'y': point[1] - bounds_rect['top']} for point in polygon]

    def calc_hotspots(self, scene, cam):
        wr360Config = scene.wr360Config
        frame_hotspots = []
        # TODO: move evaluated_depsgraph_get before the loop that calls calc_hotspots
        depth_graph = bpy.context.evaluated_depsgraph_get()
        
        for hotspot in self.hotspots:
            obj = hotspot['obj']
            hotspot_type = obj['wr360HotspotType']
            hotspot_name = hotspot['name']  
            group_xy = [] 
            
            for coord in self.get_hotspot_coords(hotspot, scene, cam):
                if hotspot_type == 'poly_mesh' or hotspot_type == 'poly':
                    is_visible = self.is_mesh_coord_visible(depth_graph, coord['v'], scene, cam) 
                else:
                    is_visible = self.is_empty_coord_visible(depth_graph, coord['v'], hotspot_name, scene, cam)
                
                if is_visible == False and hotspot_type != 'poly_mesh':
                    group_xy = []
                    break;
                        
                coord_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, coord['v'])
                render_scale = scene.render.resolution_percentage / 100
                render_size = (
                    int(scene.render.resolution_x * render_scale), 
                    int(scene.render.resolution_y * render_scale))
               
                x = coord_2d.x * render_size[0]
                y = render_size[1] - coord_2d.y * render_size[1]
                
                if wr360Config.crop_region:
                    x = x - scene.render.border_min_x * render_size[0]
                    y = y - (1 - scene.render.border_max_y) * render_size[1]
               
                group_xy.append({
                    'x': x, 
                    'y': y, 
                    'face': coord['face'], 
                    'visible': is_visible 
                })
            
            if len(group_xy) == 0:
                continue
                
            position_data = {
                'name': hotspot_name, 
                'type': hotspot_type,
                'group_xy': group_xy
            }
            
            if hotspot_type == 'poly' or hotspot_type == 'poly_mesh':
                bound_rect = self.get_poly_bounds(group_xy)
                position_data['clip'] = bound_rect
                projection = None
                
                if self.wr360HotspotConfig.projection_type == 'quad_mesh':
                    projection = self.get_mesh_poly_merge_xy(group_xy, bound_rect)
                elif self.wr360HotspotConfig.projection_type == 'gift_wrap':
                    projection = self.get_mesh_poly_hull_xy(group_xy, bound_rect)
                elif self.wr360HotspotConfig.projection_type == 'flat_poly' and hotspot_type != 'poly_mesh':
                    projection = self.get_vgroup_poly_xy(group_xy, bound_rect)
                
                if projection:
                    position_data['group_xy'] = projection
                    frame_hotspots.append(position_data)    
            else:        
                frame_hotspots.append(position_data)    
            
        self.hotspots_positions.append(frame_hotspots)   
        
    def capture_hotspots(self, context):
        scene = context.scene
        wr360Config = scene.wr360Config
        self.hotspots = []
        self.hotspots_positions = []
        
        for obj in scene.objects:
            isHotspot = False
            if 'wr360IsHotspot' in obj:
                isHotspot = obj['wr360IsHotspot']
            if isHotspot == False:
                continue    
            hotspot_type = obj['wr360HotspotType']    
            if hotspot_type == 'empty':
                self.hotspots.append({ 'name': obj.name, 'obj': obj })
            if hotspot_type == 'poly_mesh':
                self.hotspots.append({ 'name': obj.name, 'obj': obj })    
            else:
                for vertex_group in obj.vertex_groups:
                    self.hotspots.append({ 
                        'name': vertex_group.name, 
                        'group_index': vertex_group.index,
                        'obj': obj })
            
        if len(self.hotspots) == 0:
            return
        
        total_rows = wr360Config.vertical_row_up + wr360Config.vertical_row_down + 1
        wr360_cam = scene.objects.get(wr360Config.camera_name)

        for area in bpy.context.window.screen.areas:
            if area.type == 'VIEW_3D':
                space_data = area.spaces[0]
                space_data.region_3d.view_perspective = 'CAMERA'
                
        frame_pos_hotspots = 1
        
        bpy.ops.mesh.primitive_cube_add()
        trace_cube = bpy.context.active_object
        trace_cube.name = self.ray_tracer_name
        trace_cube.scale = (0.01, 0.01, 0.01)
        
        try:
            for row_num in range(0, total_rows): 
                for frame_num in range(0, wr360Config.frame_number): 
                    scene.frame_set(frame_pos_hotspots)
                    self.calc_hotspots(scene, wr360_cam)
                    frame_pos_hotspots += 1      
        finally:
            bpy.data.objects.remove(trace_cube, do_unlink=True)
                        
    def get_skin_type(self, viewer_skin):
        if viewer_skin == 'basic':
            return 0
        elif viewer_skin == 'thin':
            return 1
        elif viewer_skin == 'round':
            return 2
        elif viewer_skin == 'empty':
            return 3
        elif viewer_skin == 'retina':
            return 4
        elif viewer_skin == 'zoom_dark':
            return 5
        elif viewer_skin == 'zoom_light':
            return 6
        return 0
        
def register():
    Scene.wr360Publisher = WR360_Publisher()     

def unregister():
    del Scene.wr360Publisher                           
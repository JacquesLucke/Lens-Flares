'''
Copyright (C) 2014 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys, os, bpy
from bpy_extras.image_utils import load_image
sys.path.append(os.path.dirname(__file__)) 
from lens_flare_utils import *


bl_info = {
    "name":        "Lens Flares",
    "description": "",
    "author":      "Jacques Lucke",
    "version":     (0, 0, 1),
    "blender":     (2, 7, 1),
    "location":    "View 3D > Tool Shelf",
    "category":    "3D View"
    }
	
imagePath = "F:\Content\Texturen\Lens Flares u. ä\Lens Flares\Acrez2.jpg"
	
def newLensFlare():
	plane = newPlane()
	camera = getActiveCamera()
	setParentWithoutInverse(plane, camera)
	plane.location.z = -1
	
	image = load_image(imagePath)
	
	material = newFlareMaterial(image)
	plane.data.materials.append(material)
	
def newFlareMaterial(image):
	material = newCyclesMaterial()
	cleanMaterial(material)
	
	nodeTree = material.node_tree
	output = newOutputNode(nodeTree)
	emission = newEmissionNode(nodeTree)
	imageNode = newImageTextureNode(nodeTree)
	transparent = newTransparentNode(nodeTree)
	mixShader = newMixShader(nodeTree)
	
	imageNode.image = image
	textureCoordinatesNode = newTextureCoordinatesNode(nodeTree)
	
	newNodeLink(nodeTree, imageNode.inputs[0], textureCoordinatesNode.outputs["Generated"])
	newNodeLink(nodeTree, emission.inputs[0], imageNode.outputs[0])
	linkToMixShader(nodeTree, transparent.outputs[0], emission.outputs[0], mixShader, factor = imageNode.outputs[0])
	newNodeLink(nodeTree, output.inputs[0], mixShader.outputs[0])
	return material
	
	
# interface

class LensFlarePanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Lens Flares"
	bl_label = "Lens Flares"
	bl_context = "objectmode"
	
	def draw(self, context):
		layout = self.layout		
		layout.operator("lens_flares.new_lens_flare")
		
		
# operators
		
class NewLensFlare(bpy.types.Operator):
	bl_idname = "lens_flares.new_lens_flare"
	bl_label = "New Lens Flare"
	bl_description = "Create new Lens Flare"
	
	def execute(self, context):
		newLensFlare()
		return{"FINISHED"}
		
			

#registration

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
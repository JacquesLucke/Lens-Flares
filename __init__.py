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

import sys, os, bpy, mathutils
from bpy.app.handlers import persistent
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
	
flareEmptyPrefix = "flare container"
flareElementPrefix = "flare element"
positionControlerPrefix = "position controler"
offsetControlerPrefix = "offset controler"

cameraCenterPrefix = "center of camera"
startElementPrefix = "start element"
worldXName = "world x"
worldYName = "world y"
worldZName = "world z"
dofDistanceName = "dof distance"
plainDistanceName = "plane distance"
directionXName = "direction x"
directionYName = "direction y"
directionZName = "direction z"
angleName = "angle"
startDistanceName = "start distance"

worldXPath = getDataPath(worldXName)
worldYPath = getDataPath(worldYName)
worldZPath = getDataPath(worldZName)
anglePath = getDataPath(angleName)
startDistancePath = getDataPath(startDistanceName)
directionXPath = getDataPath(directionXName)
directionYPath = getDataPath(directionYName)
directionZPath = getDataPath(directionZName)

#temporary
plainDistance = 4	
imagePath = "F:\Content\Texturen\Lens Flares u. ä\Lens Flares\SpotLight.png"

	
def newLensFlare():
	image = getImage(imagePath)
	
	target = getActive()
	camera = getActiveCamera()
	center = getCenterEmpty(camera)
	flareControler = newFlareControler(camera, target, center)	
	startElement = newStartElement(flareControler, camera)
	
def newFlareControler(camera, target, center):
	flareControler = newEmpty()
	setParentWithoutInverse(flareControler, camera)	
	setTargetDirectionProperties(flareControler, target)
	setTargetAngleProperty(flareControler, camera, center)
	setStartDistanceProperty(flareControler, center)
	return flareControler
def setTargetDirectionProperties(flareControler, target):
	setTransformDifferenceAsProperty(flareControler, target, directionXName, "LOC_X", normalized = True)
	setTransformDifferenceAsProperty(flareControler, target, directionYName, "LOC_Y", normalized = True)
	setTransformDifferenceAsProperty(flareControler, target, directionZName, "LOC_Z", normalized = True)
def setTargetAngleProperty(flareControler, camera, center):
	setCustomProperty(flareControler, angleName)
	driver = newDriver(flareControler, anglePath)
	linkFloatPropertyToDriver(driver, "x1", flareControler, getDataPath(directionXName))
	linkFloatPropertyToDriver(driver, "y1", flareControler, getDataPath(directionYName))
	linkFloatPropertyToDriver(driver, "z1", flareControler, getDataPath(directionZName))	
	linkFloatPropertyToDriver(driver, "x2", center, getDataPath(directionXName))
	linkFloatPropertyToDriver(driver, "y2", center, getDataPath(directionYName))
	linkFloatPropertyToDriver(driver, "z2", center, getDataPath(directionZName))
	driver.expression = "degrees(acos(x1*x2+y1*y2+z1*z2))"
def setStartDistanceProperty(flareControler, center):
	setCustomProperty(flareControler, startDistanceName)
	driver = newDriver(flareControler, startDistancePath)
	linkTransformChannelToDriver(driver, "plainDistance", center, "LOC_Z", space = "LOCAL_SPACE")
	linkFloatPropertyToDriver(driver, "angle", flareControler, anglePath)
	driver.expression = "plainDistance/cos(radians(angle))"
	
def newStartElement(flareControler, camera):
	startElement = newEmpty(name = startElementPrefix)
	setParentWithoutInverse(startElement, flareControler)
	constraint = startElement.constraints.new(type = "LIMIT_LOCATION")
	setUseMinMaxToTrue(constraint)
	constraintPath = 'constraints["' + constraint.name + '"]'
	createCopyValueDriver(startElement, constraintPath + ".min_x", startElement, constraintPath + ".max_x")
	createCopyValueDriver(startElement, constraintPath + ".min_y", startElement, constraintPath + ".max_y")
	createCopyValueDriver(startElement, constraintPath + ".min_z", startElement, constraintPath + ".max_z")
	
	driver = newDriver(startElement, constraintPath + ".min_x")
	linkFloatPropertyToDriver(driver, "direction", flareControler, directionXPath)
	linkFloatPropertyToDriver(driver, "distance", flareControler, startDistancePath)
	linkTransformChannelToDriver(driver, "cam", camera, "LOC_X")
	driver.expression = "direction*distance+cam"
	
	driver = newDriver(startElement, constraintPath + ".min_y")
	linkFloatPropertyToDriver(driver, "direction", flareControler, directionYPath)
	linkFloatPropertyToDriver(driver, "distance", flareControler, startDistancePath)
	linkTransformChannelToDriver(driver, "cam", camera, "LOC_Y")
	driver.expression = "direction*distance+cam"
	
	driver = newDriver(startElement, constraintPath + ".min_z")
	linkFloatPropertyToDriver(driver, "direction", flareControler, directionZPath)
	linkFloatPropertyToDriver(driver, "distance", flareControler, startDistancePath)
	linkTransformChannelToDriver(driver, "cam", camera, "LOC_Z")
	driver.expression = "direction*distance+cam"
	
def getCenterEmpty(camera):
	centers = getCenterEmpties()
	for center in centers:
		if center.parent == camera:
			return center
	return newCenterEmpty(camera)
def getCenterEmpties():
	centers = []
	for object in bpy.data.objects:
		if hasPrefix(object.name, cameraCenterPrefix):
			centers.append(object)
	return centers
def newCenterEmpty(camera):
	center = newEmpty(name = cameraCenterPrefix, type = "SPHERE")
	setParentWithoutInverse(center, camera)
	center.empty_draw_size = 0.1
	setWorldLocationProperties(center)
	setDistanceProperty(center, dofDistanceName, camera, getDofObject(camera))
	driver = newDriver(center, "location", index = 2)
	linkFloatPropertyToDriver(driver, "var", center, getDataPath(dofDistanceName))
	driver.expression = "-var"
	setCameraDirectionProperties(center, camera)
	return center
def setWorldLocationProperties(object):
	setWorldTransformAsProperty(object, worldXName, "LOC_X")
	setWorldTransformAsProperty(object, worldYName, "LOC_Y")
	setWorldTransformAsProperty(object, worldZName, "LOC_Z")
def setDistanceProperty(target, propertyName, object1, object2):
	setCustomProperty(target, propertyName, 4.0)
	driver = newDriver(target, getDataPath(propertyName), type = "SUM")
	linkDistanceToDriver(driver, "var", object1, object2)
def setCameraDirectionProperties(center, camera):
	setTransformDifferenceAsProperty(center, camera, directionXName, "LOC_X", normalized = True)
	setTransformDifferenceAsProperty(center, camera, directionYName, "LOC_Y", normalized = True)
	setTransformDifferenceAsProperty(center, camera, directionZName, "LOC_Z", normalized = True)

	
	
def newFlareElement():
	image = getImage(imagePath)
	flareEmpty = getFlareEmpty()
	
	positionControler = newPositionControler()
	offsetControler = newOffsetControler()
	plain = newFlareElementPlane(image)
	
	setParentWithoutInverse(positionControler, flareEmpty)
	setParentWithoutInverse(offsetControler, positionControler)
	setParentWithoutInverse(plain, offsetControler)
	
	offsetControler.location.z = -1
	plain.location.z = getRandom(-0.01, 0.01)
	
def newPositionControler():
	positionControler = newEmpty(name = positionControlerPrefix)
	positionControler.empty_draw_size = 0.2
	return positionControler
	
def newOffsetControler():
	offsetControler = newEmpty(name = offsetControlerPrefix)
	offsetControler.empty_draw_size = 0.2014
	return offsetControler
	
def newFlareElementPlane(image):
	plane = newPlane(name = flareElementPrefix, size = 0.1)
	plane.scale.x = image.size[0] / image.size[1]
	makeOnlyVisibleToCamera(plane)
	material = newCyclesFlareMaterial(image)
	setMaterialOnObject(plane, material)
	return plane
	
def newCyclesFlareMaterial(image):
	material = newCyclesMaterial()
	cleanMaterial(material)
	
	nodeTree = material.node_tree
	textureCoordinatesNode = newTextureCoordinatesNode(nodeTree)
	imageNode = newImageTextureNode(nodeTree)
	toBw = newRgbToBwNode(nodeTree)
	mixColor = newColorMixNode(nodeTree, type = "DIVIDE", factor = 1)
	emission = newEmissionNode(nodeTree)
	transparent = newTransparentNode(nodeTree)
	mixShader = newMixShader(nodeTree)
	output = newOutputNode(nodeTree)
	
	imageNode.image = image
	
	newNodeLink(nodeTree, textureCoordinatesNode.outputs["Generated"], imageNode.inputs[0])
	newNodeLink(nodeTree, imageNode.outputs[0], toBw.inputs[0])
	newNodeLink(nodeTree, imageNode.outputs[0], mixColor.inputs[1])
	newNodeLink(nodeTree, toBw.outputs[0], mixColor.inputs[2])
	newNodeLink(nodeTree, mixColor.outputs[0], emission.inputs[0])
	linkToMixShader(nodeTree, transparent.outputs[0], emission.outputs[0], mixShader, factor = imageNode.outputs[0])
	newNodeLink(nodeTree, mixShader.outputs[0], output.inputs[0])
	return material
	
	
def getFlareEmpty():
	for object in bpy.data.objects:
		print(object.name)
		if hasPrefix(object.name, flareEmptyPrefix):
			return object
	return None
	
def getCameraFromFlareControler(flareControler):
	return flareControler.parent
	
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
		
# @persistent
# def frameChangeHandler(scene):
	# print(scene)
	# frame = scene.frame_current
	# newText(location = [getRandom(-10, 10), getRandom(-10, 10), getRandom(-10, 10)], text = str(frame))		
# bpy.app.handlers.frame_change_post.append(frameChangeHandler)	

#registration

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
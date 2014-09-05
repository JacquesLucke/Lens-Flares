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
from lens_flare_create_object_utils import *
from lens_flare_constraint_utils import *
from lens_flare_driver_utils import *
from lens_flare_animation_utils import *
from lens_flare_material_and_node_utils import *


bl_info = {
    "name":        "Lens Flares",
    "description": "",
    "author":      "Jacques Lucke",
    "version":     (0, 0, 1),
    "blender":     (2, 7, 1),
    "location":    "View 3D > Tool Shelf",
    "category":    "3D View"
    }
	
flareControlerPrefix = "flare controler"
angleCalculatorPrefix = "angle calculator"
startDistanceCalculatorPrefix = "start distance calculator"
flareElementPrefix = "flare element"
cameraCenterPrefix = "center of camera"
startElementPrefix = "start element"
endElementPrefix = "end element"

dofDistanceName = "dof distance"
plainDistanceName = "plane distance"
directionXName = "direction x"
directionYName = "direction y"
directionZName = "direction z"
angleName = "angle"
startDistanceName = "start distance"
randomOffsetName = "random offset"
elementPositionName = "element position"

anglePath = getDataPath(angleName)
startDistancePath = getDataPath(startDistanceName)
directionXPath = getDataPath(directionXName)
directionYPath = getDataPath(directionYName)
directionZPath = getDataPath(directionZName)
dofDistancePath = getDataPath(dofDistanceName)
randomOffsetPath = getDataPath(randomOffsetName)
elementPositionPath = getDataPath(elementPositionName)

#temporary
imagePath = "F:\Content\Texturen\Lens Flares u. ä\Lens Flares\SpotLight.png"

# new lens flare
###################################

def newLensFlare():
	image = getImage(imagePath)
	
	target = getActive()
	camera = getActiveCamera()
	center = getCenterEmpty(camera)
	flareControler = newFlareControler(camera, target, center)	
	angleCalculator = newAngleCalculator(flareControler, camera, target, center)
	startDistanceCalculator = newStartDistanceCalculator(flareControler, angleCalculator, center)
	
	startElement = newStartElement(flareControler, camera, startDistanceCalculator)
	endElement = newEndElement(flareControler, startElement, center, camera)
	
	angleCalculator.hide = True
	startDistanceCalculator.hide = True

# center creation	

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
	lockCurrentLocalLocation(center, zAxes = False)
	linkCenterDistanceToLocation(center, camera, getDofObject(camera))
	setCameraDirectionProperties(center, camera)
	return center
	
def linkCenterDistanceToLocation(center, camera, dof):
	driver = newDriver(center, "location", index = 2)
	linkDistanceToDriver(driver, "var", camera, dof)
	driver.expression = "-var"
	
def setCameraDirectionProperties(center, camera):
	setTransformDifferenceAsProperty(center, camera, directionXName, "LOC_X", normalized = True)
	setTransformDifferenceAsProperty(center, camera, directionYName, "LOC_Y", normalized = True)
	setTransformDifferenceAsProperty(center, camera, directionZName, "LOC_Z", normalized = True)
	
# flare controler creation	

def newFlareControler(camera, target, center):
	flareControler = newEmpty(name = flareControlerPrefix)
	setParentWithoutInverse(flareControler, camera)	
	lockCurrentLocalLocation(flareControler)
	setTargetDirectionProperties(flareControler, target)
	return flareControler
	
def setTargetDirectionProperties(flareControler, target):
	setTransformDifferenceAsProperty(flareControler, target, directionXName, "LOC_X", normalized = True)
	setTransformDifferenceAsProperty(flareControler, target, directionYName, "LOC_Y", normalized = True)
	setTransformDifferenceAsProperty(flareControler, target, directionZName, "LOC_Z", normalized = True)
	
# angle calculator

def newAngleCalculator(flareControler, camera, target, center):
	angleCalculator = newEmpty(name = angleCalculatorPrefix)
	setParentWithoutInverse(angleCalculator, flareControler)
	setTargetAngleProperty(angleCalculator, flareControler, center)
	setStartDistanceProperty(angleCalculator, flareControler, center)
	return angleCalculator
	
def setTargetAngleProperty(angleCalculator, flareControler, center):
	setCustomProperty(angleCalculator, angleName)
	driver = newDriver(angleCalculator, anglePath)
	linkFloatPropertyToDriver(driver, "x1", flareControler, directionXPath)
	linkFloatPropertyToDriver(driver, "y1", flareControler, directionYPath)
	linkFloatPropertyToDriver(driver, "z1", flareControler, directionZPath)	
	linkFloatPropertyToDriver(driver, "x2", center, directionXPath)
	linkFloatPropertyToDriver(driver, "y2", center, directionYPath)
	linkFloatPropertyToDriver(driver, "z2", center, directionZPath)
	driver.expression = "degrees(acos(x1*x2+y1*y2+z1*z2))"
	
# start distance calculator
	
def newStartDistanceCalculator(flareControler, angleCalculator, center):
	startDistanceCalculator = newEmpty(name = startDistanceCalculatorPrefix)
	setParentWithoutInverse(startDistanceCalculator, flareControler)
	setStartDistanceProperty(startDistanceCalculator, angleCalculator, center)
	return startDistanceCalculator
	
def setStartDistanceProperty(startDistanceCalculator, angleCalculator, center):
	setCustomProperty(startDistanceCalculator, startDistanceName)
	driver = newDriver(startDistanceCalculator, startDistancePath)
	linkTransformChannelToDriver(driver, "plainDistance", center, "LOC_Z", space = "LOCAL_SPACE")
	linkFloatPropertyToDriver(driver, "angle", angleCalculator, anglePath)
	driver.expression = "plainDistance/cos(radians(angle))"

# start element creation
	
def newStartElement(flareControler, camera, startDistanceCalculator):
	startElement = newEmpty(name = startElementPrefix)
	setParentWithoutInverse(startElement, flareControler)
	setStartLocationDrivers(startElement, camera, flareControler, startDistanceCalculator)
	return startElement
	
def setStartLocationDrivers(startElement, camera, flareControler, startDistanceCalculator):
	constraint = startElement.constraints.new(type = "LIMIT_LOCATION")
	setUseMinMaxToTrue(constraint)
	constraintPath = 'constraints["' + constraint.name + '"]'
	
	for val in [".min", ".max"]:
		driver = newDriver(startElement, constraintPath + val + "_x")
		linkFloatPropertyToDriver(driver, "direction", flareControler, directionXPath)
		linkFloatPropertyToDriver(driver, "distance", startDistanceCalculator, startDistancePath)
		linkTransformChannelToDriver(driver, "cam", camera, "LOC_X")
		driver.expression = "direction*distance+cam"
		
		driver = newDriver(startElement, constraintPath + val + "_y")
		linkFloatPropertyToDriver(driver, "direction", flareControler, directionYPath)
		linkFloatPropertyToDriver(driver, "distance", startDistanceCalculator, startDistancePath)
		linkTransformChannelToDriver(driver, "cam", camera, "LOC_Y")
		driver.expression = "direction*distance+cam"
		
		driver = newDriver(startElement, constraintPath + val + "_z")
		linkFloatPropertyToDriver(driver, "direction", flareControler, directionZPath)
		linkFloatPropertyToDriver(driver, "distance", startDistanceCalculator, startDistancePath)
		linkTransformChannelToDriver(driver, "cam", camera, "LOC_Z")
		driver.expression = "direction*distance+cam"
	
# end element creation

def newEndElement(flareControler, startElement, center, camera):
	endElement = newEmpty(name = endElementPrefix)
	setParentWithoutInverse(endElement, flareControler)
	setEndLocationDrivers(endElement, startElement, center)
	return endElement
	
def setEndLocationDrivers(endElement, startElement, center):
	constraint = endElement.constraints.new(type = "LIMIT_LOCATION")
	setUseMinMaxToTrue(constraint)
	constraintPath = 'constraints["' + constraint.name + '"]'

	for val in [".min", ".max"]:
		driver = newDriver(endElement, constraintPath + val + "_x")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_X")
		linkTransformChannelToDriver(driver, "center", center, "LOC_X")
		driver.expression = "2*center - start"
		
		driver = newDriver(endElement, constraintPath + val + "_y")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_Y")
		linkTransformChannelToDriver(driver, "center", center, "LOC_Y")
		driver.expression = "2*center - start"
		
		driver = newDriver(endElement, constraintPath + val + "_z")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_Z")
		linkTransformChannelToDriver(driver, "center", center, "LOC_Z")
		driver.expression = "2*center - start"
	
	

# new element
#########################################
	
def newFlareElement():
	image = getImage(imagePath)
	flareControler = getActiveFlareControler()
	startElement = getStartElement(flareControler)
	endElement = getEndElement(flareControler)
	
	flareElement = newFlareElementPlane(image)	
	setParentWithoutInverse(flareElement, flareControler)
	setCustomProperty(flareElement, randomOffsetName, getRandom(-0.01, 0.01))
	setCustomProperty(flareElement, elementPositionName, 0.2)
	
	constraint = flareElement.constraints.new(type = "LIMIT_LOCATION")
	setUseMinMaxToTrue(constraint)
	constraintPath = 'constraints["' + constraint.name + '"]'
	
	for val in [".min", ".max"]:
		driver = newDriver(flareElement, constraintPath + val + "_x")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_X")
		linkTransformChannelToDriver(driver, "end", endElement, "LOC_X")
		linkFloatPropertyToDriver(driver, "position", flareElement, elementPositionPath)
		linkFloatPropertyToDriver(driver, "random", flareElement, randomOffsetPath)
		driver.expression = "start * (1-position) + end * position + random"
		
		driver = newDriver(flareElement, constraintPath + val + "_y")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_Y")
		linkTransformChannelToDriver(driver, "end", endElement, "LOC_Y")
		linkFloatPropertyToDriver(driver, "position", flareElement, elementPositionPath)
		linkFloatPropertyToDriver(driver, "random", flareElement, randomOffsetPath)
		driver.expression = "start * (1-position) + end * position + random"
		
		driver = newDriver(flareElement, constraintPath + val + "_z")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_Z")
		linkTransformChannelToDriver(driver, "end", endElement, "LOC_Z")
		linkFloatPropertyToDriver(driver, "position", flareElement, elementPositionPath)
		linkFloatPropertyToDriver(driver, "random", flareElement, randomOffsetPath)
		driver.expression = "start * (1-position) + end * position + random"
	

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
	
	
	
# utils
################################

def isFlareControlerActive():
	return getActiveFlareControler() is not None
	
def getActiveFlareControler():
	active = getActive()
	if isFlareControler(active): return active
	else: return None

def isFlareControler(object):
	if object is not None:
		if hasPrefix(object.name, flareControlerPrefix):
			return True
	return False
	
def getCameraFromFlareControler(flareControler):
	return flareControler.parent
	
def getCenterFromCamera(camera):
	for object in bpy.data.objects:
		if isCenterEmpty(object):
			if getCameraFromCenter(object) == camera:
				return True
	return False

def isCenterEmpty(object):
	return hasPrefix(object.name, cameraCenterPrefix) and isCameraObject(object.parent)
	
def getCameraFromCenter(center):
	return center.parent
	
def getStartElement(flareControler):
	for object in bpy.data.objects:
		if isStartElement(object) and object.parent == flareControler:
			return object
	return None
	
def isStartElement(object):
	return hasPrefix(object.name, startElementPrefix) and isFlareControler(object.parent)
	
def getEndElement(flareControler):
	for object in bpy.data.objects:
		if isEndElement(object) and object.parent == flareControler:
			return object
	return None
	
def isEndElement(object):
	return hasPrefix(object.name, endElementPrefix) and isFlareControler(object.parent)
	
	
	
# interface
##################################

class LensFlarePanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Lens Flares"
	bl_label = "Lens Flares"
	bl_context = "objectmode"
	
	def draw(self, context):
		layout = self.layout		
		layout.operator("lens_flares.new_lens_flare")
		layout.operator("lens_flares.new_flare_element")
		
		
		
# operators
###################################
		
class NewLensFlare(bpy.types.Operator):
	bl_idname = "lens_flares.new_lens_flare"
	bl_label = "New Lens Flare"
	bl_description = "Create a new Lens Flare."
	
	def execute(self, context):
		newLensFlare()
		return{"FINISHED"}
		
class NewFlareElement(bpy.types.Operator):
	bl_idname = "lens_flares.new_flare_element"
	bl_label = "New Flare Element"
	bl_description = "Create a new Element in active Lens Flare."
	
	@classmethod
	def poll(self, context):
		return isFlareControlerActive()
	
	def execute(self, context):
		newFlareElement()
		return{"FINISHED"}
		
		
		
# register
##################################

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
import pyblish.api
from maya import cmds

import pyblish_magenta.utils.maya.context as maya_context


class ValidateMeshNonZeroFaceArea(pyblish.api.Validator):
    """ Validate meshes don't have zero area faces.

        .. note:: This can be slow for high-res meshes.

        Also see: http://help.autodesk.com/view/MAYAUL/2015/ENU/?guid=Mesh__Cleanup """
    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)

    __tolerance = 1e-8

    def process(self, instance):
        """ Process all meshes """
        meshes = cmds.ls(instance, type='mesh', dag=True, long=True)

        result = []
        with maya_context.PreserveSelection():
            # Select all faces
            faces = ['{0}.f[*]'.format(node) for node in meshes]
            cmds.select(faces, r=1)

            # Get filtered faces
            with maya_context.TemporaryPolySelectConstraint(disable=True,  # Disable previous settings, use only current
                                                            mode=3,        # mode: All and Next
                                                            t=8,           # type: 0x0008(face)
                                                            geometricarea=1,
                                                            geometricareabound=(0, self.__tolerance)):
                result = cmds.ls(sl=1)

        if result:
            raise RuntimeError("Meshes found with zero face areas: {0}".format(result))

        #raise NotImplementedError("Needs to be implemented")

        # This is how polyCleanup does it: #
        # // Get zero area geometry faces
        # if ($fgeom)
        # {
        # 	select -r $selectedItems;
        # 	//print ("Select geom faces between " + $minface + " " + $maxface + "\n");
        #     polySelectConstraint -m 3 -t 8 -ga on -gab $minface $maxface;
        # 	$selected = `ls -sl`;
        # 	concat( $zeroFaces, $selected );
        # 	polySelectConstraint -m 0 -t 8 -ga off;
        # }
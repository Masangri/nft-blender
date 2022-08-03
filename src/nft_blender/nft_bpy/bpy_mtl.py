#!$BLENDER_PATH/python/bin python

"""
NFT Blender - BPY - MTL

"""

import json
import pathlib
import re
import typing

import bpy


# Load default data from config file.
bpy_mtl_config_file_path = pathlib.Path(__file__).parent.joinpath('bpy_mtl.config.json')
with bpy_mtl_config_file_path.open('r', encoding='UTF-8') as readfile:
    MTL_PBR_PREFS = json.load(readfile)


def mtl_search_replace_image_dir_paths(
    search_for: str = '',
    replace_with: str = '',
    collection: bpy.types.Collection = None,
) -> list:
    """
    Searches and replaces a substring in the file path for Image nodes.

    :param search_for: Substring to search for.
    :param replace_with: Substring to be used as a replacement.
    :param collection: If a Collection is given,
        only Image nodes for Materials applied to Mesh objects in the Collection are affected.
    :returns: A list of updated Image nodes.
    """
    updated_img_nodes = []

    if collection:
        img_nodes, mtl_list = [], []
        mesh_objs = (obj for obj in collection.all_objects if obj.type == 'MESH')
        for mesh_obj in mesh_objs:
            for mtl in mesh_obj.data.materials:
                if mtl not in mtl_list:
                    for grp in (n for n in mtl.node_tree.nodes if n.type == 'GROUP'):
                        for tex_img in (n for n in grp.node_tree.nodes if n.type == 'TEX_IMAGE'):
                            img_nodes.append(tex_img.image)
                    for tex_img in (n for n in mtl.node_tree.nodes if n.type == 'TEX_IMAGE'):
                        img_nodes.append(tex_img.image)
                mtl_list.append(mtl)

    else:
        img_nodes = bpy.data.images

    re_img_data_pattern = re.compile(
        fr'^.+_(?P<img_data_name>({"|".join(MTL_PBR_PREFS.keys())}))\.(?P<ext>\w+)$'
    )

    for img_node in img_nodes:

        repathed_fp = pathlib.Path(img_node.filepath.replace(search_for, replace_with))
        re_match = re_img_data_pattern.match(repathed_fp.as_posix())

        if re_match:

            img_suffix = re_match.group('img_data_name')
            colorspace_settings = MTL_PBR_PREFS.get(img_suffix)['colorspace_settings']

            repathed_fp_str = '//' + str(repathed_fp).lstrip('\\')
            img_node.filepath = repathed_fp_str
            img_node.colorspace_settings.name = colorspace_settings

            updated_img_nodes.append(img_node)

    return updated_img_nodes


def mtl_set_material_data(
    mtl_name: str = '',
    mesh_objs: typing.Iterable = (),
) -> bool:
    """
    Sets the active Material for the given Mesh objects.

    :param mtl_name: The name of the Material to set as the active Material.
    :param mesh_objs: The Mesh objects to set.
    :returns: True if Material data was assigned to at least one Mesh; otherwise False.
    """
    mtl = bpy.data.materials.get(mtl_name)
    mtl_assigned = False

    if mtl:
        for mesh_obj in (obj for obj in mesh_objs if obj.type == 'MESH'):
            mesh_obj.active_material = mtl
        mtl_assigned = True

    return mtl_assigned
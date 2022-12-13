#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "Luca Monari"
__credits__ = ["Luca Monari"]
__version__ = "1.0"
__email__ = "luca.monari@etu.unistra.fr"

import numpy as np
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from pdf2image import convert_from_path  # require poppler
import rdkit
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import rdCoordGen
from rdkit.Chem import rdDepictor
import math
from scipy.spatial.transform import Rotation as Rot
from scipy.linalg import norm
import plotly.graph_objects as go
import argparse
import os
import colorsys
import warnings
import requests
from io import BytesIO
import xml.etree.ElementTree as ET

warnings.filterwarnings("ignore")  # brute force approach to avoid decompression bomb warning by pdf2image and PIL

# dictionary containing the default colour for each atom, according to CPK colour convention
color_map = {"H": "#FFFFFF", "D": "#FFFFC0", "T": "#FFFFA0", "He": "#D9FFFF", "Li": "#CC80FF", "Be": "#C2FF00",
             "B": "#FFB5B5", "C": "#909090", "C-13": "#505050", "C-14": "#404040", "N": "#3050F8", "N-15": "#105050",
             "O": "#FF0D0D", "F": "#90E050", "Ne": "#B3E3F5", "Na": "#AB5CF2", "Mg": "#8AFF00", "Al": "#BFA6A6",
             "Si": "#F0C8A0", "P": "#FF8000", "S": "#FFFF30", "Cl": "#1FF01F", "Ar": "#80D1E3", "K": "#8F40D4",
             "Ca": "#3DFF00", "Sc": "#E6E6E6", "Ti": "#BFC2C7", "V": "#A6A6AB", "Cr": "#8A99C7", "Mn": "#9C7AC7",
             "Fe": "#E06633", "Co": "#F090A0", "Ni": "#50D050", "Cu": "#C88033", "Zn": "#7D80B0", "Ga": "#C28F8F",
             "Ge": "#668F8F", "As": "#BD80E3", "Se": "#FFA100", "Br": "#A62929", "Kr": "#5CB8D1", "Rb": "#702EB0",
             "Sr": "#00FF00", "Y": "#94FFFF", "Zr": "#94E0E0", "Nb": "#73C2C9", "Mo": "#54B5B5", "Tc": "#3B9E9E",
             "Ru": "#248F8F", "Rh": "#0A7D8C", "Pd": "#006985", "Ag": "#C0C0C0", "Cd": "#FFD98F", "In": "#A67573",
             "Sn": "#668080", "Sb": "#9E63B5", "Te": "#D47A00", "I": "#940094", "Xe": "#429EB0", "Cs": "#57178F",
             "Ba": "#00C900", "La": "#70D4FF", "Ce": "#FFFFC7", "Pr": "#D9FFC7", "Nd": "#C7FFC7", "Pm": "#A3FFC7",
             "Sm": "#8FFFC7", "Eu": "#61FFC7", "Gd": "#45FFC7", "Tb": "#30FFC7", "Dy": "#1FFFC7", "Ho": "#00FF9C",
             "Er": "#00E675", "Tm": "#00D452", "Yb": "#00BF38", "Lu": "#00AB24", "Hf": "#4DC2FF", "Ta": "#4DA6FF",
             "W": "#2194D6", "Re": "#267DAB", "Os": "#266696", "Ir": "#175487", "Pt": "#D0D0E0", "Au": "#FFD123",
             "Hg": "#B8B8D0", "Tl": "#A6544D", "Pb": "#575961", "Bi": "#9E4FB5", "Po": "#AB5C00", "At": "#754F45",
             "Rn": "#428296", "Fr": "#420066", "Ra": "#007D00", "Ac": "#70ABFA", "Th": "#00BAFF", "Pa": "#00A1FF",
             "U": "#008FFF", "Np": "#0080FF", "Pu": "#006BFF", "Am": "#545CF2", "Cm": "#785CE3", "Bk": "#8A4FE3",
             "Cf": "#A136D4", "Es": "#B31FD4", "Fm": "#B31FBA", "Md": "#B30DA6", "No": "#BD0D87", "Lr": "#C70066",
             "Rf": "#CC0059", "Db": "#D1004F", "Sg": "#D90045", "Bh": "#E00038", "Hs": "#E6002E", "Mt": "#EB0026",
             'other': '#f5c2cb', 'Bond': '#979797', 'All icon': "#000000", 'All atoms': "#000000"}

# dictionary containing the value to multiply to the final radius of each atom
atom_resize = {'All atoms': 1.0, 'H': 1.0, 'D': 1.0, 'T': 1.0, 'He': 1.0, 'Li': 1.0, 'Be': 1.0, 'B': 1.0, 'C': 1.0,
               'C-13': 1.0, 'C-14': 1.0, 'N': 1.0, 'N-15': 1.0, 'O': 1.0, 'F': 1.0, 'Ne': 1.0, 'Na': 1.0, 'Mg': 1.0,
               'Al': 1.0, 'Si': 1.0, 'P': 1.0, 'S': 1.0, 'Cl': 1.0, 'Ar': 1.0, 'K': 1.0, 'Ca': 1.0, 'Sc': 1.0,
               'Ti': 1.0, 'V': 1.0, 'Cr': 1.0, 'Mn': 1.0, 'Fe': 1.0, 'Co': 1.0, 'Ni': 1.0, 'Cu': 1.0, 'Zn': 1.0,
               'Ga': 1.0, 'Ge': 1.0, 'As': 1.0, 'Se': 1.0, 'Br': 1.0, 'Kr': 1.0, 'Rb': 1.0, 'Sr': 1.0, 'Y': 1.0,
               'Zr': 1.0, 'Nb': 1.0, 'Mo': 1.0, 'Tc': 1.0, 'Ru': 1.0, 'Rh': 1.0, 'Pd': 1.0, 'Ag': 1.0, 'Cd': 1.0,
               'In': 1.0, 'Sn': 1.0, 'Sb': 1.0, 'Te': 1.0, 'I': 1.0, 'Xe': 1.0, 'Cs': 1.0, 'Ba': 1.0, 'La': 1.0,
               'Ce': 1.0, 'Pr': 1.0, 'Nd': 1.0, 'Pm': 1.0, 'Sm': 1.0, 'Eu': 1.0, 'Gd': 1.0, 'Tb': 1.0, 'Dy': 1.0,
               'Ho': 1.0, 'Er': 1.0, 'Tm': 1.0, 'Yb': 1.0, 'Lu': 1.0, 'Hf': 1.0, 'Ta': 1.0, 'W': 1.0, 'Re': 1.0,
               'Os': 1.0, 'Ir': 1.0, 'Pt': 1.0, 'Au': 1.0, 'Hg': 1.0, 'Tl': 1.0, 'Pb': 1.0, 'Bi': 1.0, 'Po': 1.0,
               'At': 1.0, 'Rn': 1.0, 'Fr': 1.0, 'Ra': 1.0, 'Ac': 1.0, 'Th': 1.0, 'Pa': 1.0, 'U': 1.0, 'Np': 1.0,
               'Pu': 1.0, 'Am': 1.0, 'Cm': 1.0, 'Bk': 1.0, 'Cf': 1.0, 'Es': 1.0, 'Fm': 1.0, 'Md': 1.0, 'No': 1.0,
               'Lr': 1.0, 'Rf': 1.0, 'Db': 1.0, 'Sg': 1.0, 'Bh': 1.0, 'Hs': 1.0, 'Mt': 1.0, 'other': 1.0}


def hex_to_rgb(color):
    """It takes a hexadecimal color string and returns a rgb tuple.

    Parameters
    ----------
    color : string
        The hexadecimal color code, it starts with a '#'.

    Returns
    -------
    tuple
        the RGB values of the hexadecimal color code.

    """
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:], 16)
    return r, g, b


def rgb_to_hex(color):
    """It takes the rgb tuple and returns the hexadecimal string of the color.
    Based on https://stackoverflow.com/questions/3380726/converting-an-rgb-color-tuple-to-a-hexidecimal-string

    Parameters
    ----------
    color : tuple
        a tuple of three integers, each between 0 and 255, representing the rgb values.

    Returns
    -------
    string
        The hexadecimal color code, it starts with a '#'.

    """
    int_color = tuple([int(x) for x in color])
    return '#%02x%02x%02x' % int_color


def shadow_color_correction(color, light_multiplier):
    """Given a color and a light multiplier, return the hexadecimal color code with the corrected light.

    Parameters
    ----------
    color : tuple
        The rgb color tuple.
    light_multiplier : float
        The value to multiply to decrease the light.

    Returns
    -------
    string
        The hexadecimal color code, it starts with a '#'.

    """
    r, g, b = hex_to_rgb(color)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    rgb = colorsys.hls_to_rgb(h, l * light_multiplier, s)
    return rgb_to_hex(rgb)


def position_map(mol, conf, rotation=(0, 0, 0)):
    """This function takes a mol object, the conformation, the position multiplier and the image dimension and calculate
    the corrected positions for the image.

    Parameters
    ----------
    mol : Mol rdkit object
        The rdkit mol object representing a molecule.
    conf : Conformer rdkit object
        The conformation of the
    rotation : tuple, default: (0,0,0)
        Tuple containing the angle (in degree) of the x-axis, y-axis and z-axis to rotate the molecule.

    Returns
    -------
    dictionary
        A dictionary in which the keys are the atom indexes and the values are the corrected positions of the atoms.
    dimension
        The half dimension of the image.

    """
    rotate = Rot.from_euler('xyz', rotation, degrees=True)
    pos_dict = dict()
    max_pos_set = set()
    for i in range(mol.GetNumAtoms()):
        # add dimension to center with respect to the center of the blank image
        pos = conf.GetAtomPosition(i)
        new_pos = rotate.apply((pos.x, pos.y, pos.z))
        pos_dict[i] = new_pos
        max_pos_set.add(max(abs(new_pos[:2])))
    bond_map = {atom_idx: set() for atom_idx in pos_dict}
    for bond in mol.GetBonds():
        bond_idx = bond.GetIdx()
        bond_map[bond.GetBeginAtomIdx()].add(bond_idx)
        bond_map[bond.GetEndAtomIdx()].add(bond_idx)
    return pos_dict, max(max_pos_set), bond_map


def circ_post(degree, size, center):
    """This function takes in an angle, size, and center and returns the x-y coordinates of the point
    on the circumference.

    Parameters
    ----------
    degree : float
        The degree angle where you want to calculate the coordinate on the circumference.
    size : float
        The radius of the circumference.
    center : tuple
        Tuple containing the x-y coordinates of the center of the circumference.

    Returns
    -------
    tuple
        A tuple with the x-y coordinates of the point on the circumference at the defined angle.

    """
    angle_rad = math.radians(degree)
    x = int(size * math.cos(angle_rad) + center[0])
    y = int(size * math.sin(angle_rad) + center[1])
    return x, y


def sphere(x, y, z, radius, resolution=20):
    """This function takes 3D coordinates and a radius a build the mesh-grid for a sphere with the defined resolution.
    Based on https://stackoverflow.com/questions/70977042/how-to-plot-spheres-in-3d-with-plotly-or-another-library

    Parameters
    ----------
    x : float
        The x-coordinates of the center of the sphere.
    y : float
        The y-coordinates of the center of the sphere.
    z : float
        The z-coordinates of the center of the sphere.
    radius : float
        The radius of the sphere.
    resolution : int, default: 20
        The number of point for each coordinate of the grid.

    Returns
    -------
    tuple
        A tuple with the x, y and z arrays to build a spherical grid.

    """
    u, v = np.mgrid[0:2 * np.pi:resolution * 2j, 0:np.pi:resolution * 1j]
    x_grid = radius * np.cos(u) * np.sin(v) + x
    y_grid = radius * np.sin(u) * np.sin(v) + y
    z_grid = radius * np.cos(v) + z
    return x_grid, y_grid, z_grid


def cylinder(radius, start, end, resolution=100):
    """This function takes a radius, a starting point (3D coordinates) and an ending point to build the mesh-grid for a
     cylinder with the defined resolution.
     Based on https://community.plotly.com/t/draw-3d-cylinder-along-points/57382

    Parameters
    ----------
    radius : float
        The radius of the cylinder.
    start : array
        The starting point of the cylinder axis (3D coordinates).
    end : array
        The ending point of the cylinder axis (3D coordinates).
    resolution : int, default: 100
        The number of point for each coordinate of the grid.

    Returns
    -------
    tuple
        A tuple with the x, y and z arrays to build a cylindrical grid.

    """
    v = end - start
    # find magnitude of vector
    mag = norm(v)
    # unit vector in direction of axis
    v = v / mag
    # create a different vector
    not_v = end - np.array((start[0] + 1, start[1], start[2]))
    # make vector perpendicular to v
    n1 = np.cross(v, not_v)
    n1 /= norm(n1)  # normalize the perpendicular vector
    # make unit vector perpendicular to v and n1
    n2 = np.cross(v, n1)
    # surface ranges over t from 0 to length of axis and 0 to 2*pi
    t = np.linspace(0, mag, resolution)
    theta = np.linspace(0, 2 * np.pi, resolution)
    # use meshgrid to make 2d arrays
    t, theta = np.meshgrid(t, theta)
    # generate coordinates for surface
    x, y, z = [start[i] + v[i] * t + radius * np.sin(theta) * n1[i] + radius * np.cos(theta) * n2[i] for i in [0, 1, 2]]
    return x, y, z


def add_atom_svg(src, center, radius, color, shadow=True, shadow_curve=1.125, shadow_deg=45, shadow_light=0.35,
                 thickness=1 / 3):
    """It draws a circle, filled with the color, in the svg text. A shadow can be drawn on the circle.

    Parameters
    ----------
    src : list
        List containing the svg text elements.
    center : tuple
        The center of the atom in x-y coordinates.
    radius : float
        The radius of the circle.
    color : string
        The hex color to fill the circle.
    shadow : bool, default: True
        Whether to add a shadow or not on the circle.
    shadow_curve : float, default: 1.125
        The curve of the shadow. 1.125 is a good value.
    shadow_deg : float, default: 45
        The angle in the degree of the shadow start.
    shadow_light : float, default: 0.35
        The lightness of the shadow. 0 is black, 1 is white.
    thickness : float, default: 1/3
        The thickness of the border of the circle.

    """
    shadow_color = shadow_color_correction(color, shadow_light)
    atom_elem = ET.Element('circle')
    atom_elem.set('cx', f'{center[0]}')
    atom_elem.set('cy', f'{center[1]}')
    atom_elem.set('r', f'{radius}')
    atom_elem.set('fill', f'{color}')
    atom_elem.set('stroke', f'{shadow_color}')
    atom_elem.set('stroke-width', f'{radius * thickness / 2}')
    src.append(atom_elem)
    if shadow:
        start_shade = circ_post(-shadow_deg, radius, center)
        end_shade = circ_post(-shadow_deg + 180, radius, center)
        shad_elem = ET.Element('path')
        shad_elem.set('d', f'M{start_shade[0]},{start_shade[1]} A{radius},{radius} 0, 1,1 {end_shade[0]},{end_shade[1]} M{end_shade[0]},{end_shade[1]} A{radius * shadow_curve},{radius * shadow_curve} 0, 0,0 {start_shade[0]}, {start_shade[1]} Z')
        shad_elem.set('fill', f'{shadow_color}')
        shad_elem.set('stroke-width', '0')
        src.append(shad_elem)
        # patch to cover line that appears in jpeg and png images with pdf2image
        start_patch = circ_post(-shadow_deg, radius - radius * thickness / 4, center)
        end_patch = circ_post(-shadow_deg + 180, radius - radius * thickness / 4, center)
        patch_elem = ET.Element('path')
        patch_elem.set('d', f'M{start_patch[0]},{start_patch[1]} L {end_patch[0]},{end_patch[1]}')
        patch_elem.set('stroke', f'{color}')
        src.append(patch_elem)


def add_bond_svg(src, bond_type, x1, y1, x2, y2, line_thickness, bondcolor='#575757', shadow_light=0.35):
    """It adds a line as a bond to an SVG image.

    Parameters
    ----------
    src : list
        List containing the svg text elements.
    bond_type : int
        The type of the bond. 1 stands for single bond, 2 stands for double bond, 3 stands for triple bond.
    x1 : float
        x-coordinate of the first atom.
    y1 : float
        y-coordinate of the first atom.
    x2 : float
        x-coordinate of the second atom.
    y2 : float
        y-coordinate of the second atom.
    line_thickness: float
        The thickness of the bond line.
    bondcolor : string, default: '#575757'
        The hex color of the bond.
    shadow_light : float, default: 0.35
        The lightness of the shadow. 0 is black, 1 is white.

    """
    start = np.array((x1, y1))
    end = np.array((x2, y2))
    d_space = line_thickness * 1.5
    t_space = line_thickness * 2.5
    # calculate the degree of the bond line, y-axis is reversed in images
    radians = math.atan2(-y1 + y2, x1 - x2) + math.pi / 2  # add 90 degree to make the angle perpendicular
    contour_color = shadow_color_correction(bondcolor, shadow_light)

    def dist_point(point, spacer):
        """This function takes a point and a spacer distance. It returns two points that have a distance
        equal to the spacer on the direction defined by the radians parent variable.

        Parameters
        ----------
        point : tuple
            A tuple of the x and y coordinates of the point.
        spacer : float
            The distance between the points.

        Returns
        -------
        tuple
            Two points with a spacer distance from point on the radian angle direction.

        """
        dist_x = int(math.cos(radians) * spacer)
        dist_y = int(math.sin(radians) * spacer)
        # y-axis is reversed in images
        pt1 = point + np.array((dist_x, -dist_y))
        pt2 = point - np.array((dist_x, -dist_y))
        return pt1, pt2

    def add_bond(p, q, thick=1, color=bondcolor):
        """It adds a bond between two points.

        Parameters
        ----------
        p : tuple
            The first point.
        q : tuple
            The second point.
        thick : float, default: 1
            The thickness multiplier of the line.
        color : str, default: bondcolor
            The hex code for the color of the bond.
        """
        bond_elem = ET.Element('line')
        bond_elem.set('stroke', f"{color}")
        bond_elem.set('stroke-linecap', "round")
        bond_elem.set('stroke-width', f'{line_thickness * thick}')
        bond_elem.set('x1', f'{p[0]}')
        bond_elem.set('y1', f'{p[1]}')
        bond_elem.set('x2', f'{q[0]}')
        bond_elem.set('y2', f'{q[1]}')
        src.append(bond_elem)

    if bond_type == 2:
        start_1, start_2 = dist_point(start, d_space)
        end_1, end_2 = dist_point(end, d_space)
        add_bond(start_1, end_1, 2, contour_color)
        add_bond(start_2, end_2, 2, contour_color)
        add_bond(start_1, end_1)
        add_bond(start_2, end_2)
    else:
        add_bond(start, end, 2, contour_color)
        add_bond(start, end)
    if bond_type == 3:
        start_1, start_2 = dist_point(start, t_space)
        end_1, end_2 = dist_point(end, t_space)
        add_bond(start_1, end_1, 2, contour_color)
        add_bond(start_2, end_2, 2, contour_color)
        add_bond(start_1, end_1)
        add_bond(start_2, end_2)


def add_emoji(src, xy, size, unicode, color=True):
    """This function a svg source and insert the unicode emoji in position xy with roughly dimension size.

    Parameters
    ----------
    src : list
        List containing the svg text elements.
    xy : tuple,
        Tuple containing x and y coordinates of the atom to replace.
    size : float
        The size of the atom to replace.
    unicode : str
        The unicode string of the emoji.
    color : bool, default: True
        Whether to use a colored or black emoji.

    """
    unicode = unicode.strip()  # just to make sure
    if color:
        url = f"https://raw.github.com/hfg-gmuend/openmoji/master/color/svg/{unicode}.svg"
    else:
        url = f"https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/black/svg/{unicode}.svg"
    response = requests.get(url)
    emoji_text = BytesIO(response.content).read().decode('utf-8')
    if emoji_text == '404: Not Found':
        raise ValueError(f'Emoji unicode ({unicode}) not found')
    root = ET.fromstring(emoji_text)
    emoji_dim = [float(i) for i in root.get("viewBox").split()]
    del root.attrib["viewBox"]
    scale_x = size / emoji_dim[2] * 3  # *3 because otherwise square emojis could be small
    scale_y = size / emoji_dim[3] * 3  # *3 because otherwise square emojis could be small
    trans_x = xy[0] - emoji_dim[2] * scale_x / 2
    trans_y = xy[1] - emoji_dim[3] * scale_y / 2
    emoji_elem = ET.Element('g')
    emoji_elem.set('transform', f'translate({trans_x} {trans_y}) scale({scale_x} {scale_y})')
    emoji_elem.append(root)
    src.append(emoji_elem)


def parse_structure(smiles, remove_H=True, nice_conformation=True, dimension_3=False, n_conf=1, force_field='UFF',
                    randomseed=-1):
    """This function takes a SMILES string and returns molecule object that hase been prepared.

    Parameters
    ----------
    smiles : string
        The SMILES string of the molecule you want to draw.
    remove_H : bool, optional
        Remove all non-chiral hydrogen from the molecule.
    nice_conformation : bool, default: True
        If True, the molecule will be put into a nice conformation.
    dimension_3 : bool, optional
        If True, it will embed and optimize a 3D structure of the molecule.
    n_conf : int, default: 1
        The number of 3D conformations to generate.
    force_field : str, default: 'UFF'
        The force field to optimize of the 3D conformation. Force fields currently supported: 'UFF' and 'MMFF'.
    randomseed: int, optional
        The value of the random seed to generate conformations.

    Returns
    -------
    mol object
        A rdkit molecule object.

    """
    mol = Chem.MolFromSmiles(smiles)  # read the molecule
    mol = Chem.AddHs(mol)  # add Hydrogens
    # build with 3D structure
    if dimension_3:
        build = AllChem.EmbedMultipleConfs(mol, numConfs=n_conf, randomSeed=randomseed)
        if build == -1:
            raise ValueError('Embedding 3D conformation failed')
        if force_field == 'UFF':
            AllChem.UFFOptimizeMoleculeConfs(mol)
        elif force_field == 'MMFF':
            AllChem.MMFFOptimizeMoleculeConfs(mol)
        # build with 2D structure
        if remove_H:
            mol = Chem.RemoveHs(mol)  # remove not chiral Hydrogens
        return mol

    # build with 2D structure
    if nice_conformation:
        rdDepictor.SetPreferCoordGen(True)  # rdCoordGen conformation as default
        rdCoordGen.AddCoords(mol)  # better conformation for macrocycle
    else:
        rdDepictor.SetPreferCoordGen(False)  # rdkit conformation default
        AllChem.Compute2DCoords(mol)  # canonical rdkit conformation
    if remove_H:
        mol = Chem.RemoveHs(mol)  # remove not chiral Hydrogen
    mol = rdkit.Chem.Draw.rdMolDraw2D.PrepareMolForDrawing(mol)  # clean the conformer
    return mol


def build_svg(mol, atom_radius=100, atom_color=color_map, radius_multi=atom_resize, pos_multi=300,
              shadow_light=0.35, shadow=False, single_bonds=False, conformation=0, thickness=1 / 4, verbose=False,
              rotation=(0, 0, 0), emoji=None):
    """This function takes a SMILES string and returns an icon of the molecule, in format PNG, SVG, JPEG, and PDF.

    Parameters
    ----------
    mol : mol object
        The rdkit mol object representing a molecule.
    atom_radius : int, default: 100
        The radius of the atoms in the icon.
    atom_color : dictionary, default: color_map
        a dictionary of atom colors. The keys are the atom symbols, and the values are the hex colors.
    radius_multi : dictionary, default: atom_resize
        A dictionary containing the multiplier for each atom. It multiplies the atom radius.
    pos_multi : int, default: 300
        This is the distance between atoms.
    shadow_light : float, default: 0.35
        How light the shadow is. 0.35 is a good value.
    shadow : bool, optional
        Whether to add a shadow to the image or not.
    single_bonds : bool, optional
        If True, all bonds will be single bonds.
    conformation : int, default: 0
        The conformation to draw.
    thickness : float, default: 1/4
        The thickness of the bonds compared to the atom radius.
    verbose : bool, optional
        Prints out the atoms and bonds coordinates.
    rotation : tuple, default: (0,0,0)
        Tuple containing the angle (in degree) of the x-axis, y-axis and z-axis to rotate the image.
    emoji : dictionary, optional
        A dictionary the string containing atom index as key, and as value a list containing the unicode
        identifier of an emoji and whether it is colored or black emoji.

    Returns
    -------
    list
        List containing the svg text elements.

    """
    conf = mol.GetConformer(conformation)
    max_radius_multi = atom_radius * max(radius_multi.values())
    pos_dict, max_pos, bond_map = position_map(mol, conf, rotation)
    # the dimension is calculated considering the maximum position, the atom diameter and multiplying by two (the
    # dimension is half of the image size
    dim = max_pos * pos_multi + max_radius_multi * 2
    # scale the position according to the image
    pos_dict = {k: val * pos_multi for k, val in pos_dict.items()}
    # setting svg attributes
    svg = ET.Element('svg')
    svg.set('id', "molecule_icon")
    svg.set('viewBox', f"{-dim} {-dim} {dim*2} {dim*2}")
    svg.set('xmlns', "http://www.w3.org/2000/svg")
    aromatic_index = set()
    bond_done = set()
    bond_thickness = int(atom_radius * thickness)
    # add atoms (to start from the Hydrogens, the atom index must be reversed)
    if verbose:
        print('\nAtom-index\tSymbol\tx\ty')
        print('\nBond-type\tAtom1\tAtom2')
    # order the atoms according to the z-axis
    atom_order = [k for k, v in sorted(pos_dict.items(), key=lambda item: item[1][2])]
    for atom_idx in atom_order:
        atom = mol.GetAtomWithIdx(atom_idx)
        symbol = atom.GetSymbol()
        # add dimension to center with respect to the center of the blank image
        atom_x = pos_dict[atom_idx][0]
        atom_y = -pos_dict[atom_idx][1]  # the y-axis is inverted in an image
        if symbol not in atom_color:
            symbol = 'other'
        if verbose:
            print(f"Atom\t{atom_idx}\t{symbol}\t{atom_x}\t{atom_y}")
        # add  atom bonds before the atom icon
        for bond_idx in bond_map[atom_idx].difference(bond_done):
            bond = mol.GetBondWithIdx(bond_idx)
            atom1 = bond.GetBeginAtom()
            idx1 = bond.GetBeginAtomIdx()
            atom2 = bond.GetEndAtom()
            idx2 = bond.GetEndAtomIdx()
            b_type = bond.GetBondType()
            if verbose:
                print(f"Bond\t{b_type}\t{idx1}\t{idx2}")
            bond_type = 1
            if rdkit.Chem.rdchem.BondType.DOUBLE == b_type and not single_bonds:
                bond_type = 2
            elif rdkit.Chem.rdchem.BondType.AROMATIC == b_type and not single_bonds:
                symbol1 = atom1.GetSymbol()
                symbol2 = atom2.GetSymbol()
                critical = ('O', 'S')
                conditions = [atom1 not in aromatic_index, atom2 not in aromatic_index,
                              symbol1 not in critical, symbol2 not in critical,
                              symbol1 != 'N' or len(bond_map[idx1]) < 3,
                              symbol2 != 'N' or len(bond_map[idx2]) < 3]
                if all(conditions):
                    bond_type = 2
                    aromatic_index.add(atom1)
                    aromatic_index.add(atom2)
            elif rdkit.Chem.rdchem.BondType.TRIPLE == b_type and not single_bonds:
                bond_type = 3
                aromatic_index.add(atom1)
                aromatic_index.add(atom2)
            add_bond_svg(svg, bond_type, pos_dict[idx1][0], -pos_dict[idx1][1], pos_dict[idx2][0], -pos_dict[idx2][1],
                         bond_thickness, bondcolor=atom_color['Bond'], shadow_light=shadow_light)
            bond_done.add(bond_idx)
        corrected_radius = atom_radius * radius_multi[symbol]  # resize the atom dimension
        if emoji and atom_idx in emoji and emoji[atom_idx][0] and emoji[atom_idx][0].strip() != '':
            add_emoji(svg, (atom_x, atom_y), corrected_radius, unicode=emoji[atom_idx][0], color=emoji[atom_idx][1])
        elif emoji and symbol in emoji and emoji[symbol][0] and emoji[symbol][0].strip() != '':
            add_emoji(svg, (atom_x, atom_y), corrected_radius, unicode=emoji[symbol][0], color=emoji[symbol][1])
        else:
            add_atom_svg(svg, (atom_x, atom_y), corrected_radius, atom_color[symbol], shadow=shadow,
                         shadow_light=shadow_light,
                         thickness=thickness)
    return svg


def icon_print(mol, name='molecule_icon', directory=os.getcwd(), rdkit_png=False, rdkit_svg=False, save_svg=True,
               save_png=False, save_jpeg=False, save_pdf=False, atom_color=color_map, atom_radius=100,
               radius_multi=atom_resize, pos_multi=300, single_bonds=False,
               shadow=True, thickness=1 / 4, shadow_light=0.35, verbose=False, rotation=(0, 0, 0), emoji=None):
    """This function takes a SMILES string and returns an icon of the molecule, in format PNG, SVG, JPEG, and PDF.

    Parameters
    ----------
    mol : mol object
        The rdkit mol object representing a molecule.
    name : string, default: 'molecule_icon'
        The name of the file to be saved.
    directory : string, default: os.getcwd()
        The directory to save the image in.
    rdkit_png : bool, optional
        If True, will use RDKit to generate a PNG image of the default structure.
    rdkit_svg : bool, optional
        If True, will use RDKit to generate an SVG image of the default structure.
    save_svg : bool, default: True
        Save the SVG icon format.
    save_png : bool, default: False
        Save the SVG, PDF and PNG icon formats.
    save_jpeg : bool, default: False
        Save the SVG, PDF and JPEG icon formats.
    save_pdf : bool, default: False
        Save the SVG and PDF icon formats.
    atom_color : dictionary, default: color_map
        A dictionary of atom colors. The keys are the atom symbols, and the values are the hex colors.
    atom_radius : int, default: 100
        The radius of the atoms in the icon.
    radius_multi : dictionary, default: atom_resize
        A dictionary containing the multiplier for each atom. It multiplies the atom radius.
    pos_multi : int, default: 300
        This is the distance between atoms.
    single_bonds : bool, optional
        If True, all bonds will be single bonds.
    shadow : bool, optional
        Whether to add a shadow to the image or not.
    thickness : float, default: 1/4
        The thickness of the bonds compared to the atom radius.
    shadow_light : float, default: 0.35
        How light the shadow is. 0.35 is a good value.
    verbose : bool, optional
        Prints out the atoms coordinates.
    rotation : tuple, default: (0,0,0)
        Tuple containing the angle (in degree) of the x-axis, y-axis and z-axis to rotate the image.
    emoji : dictionary, optional
        A dictionary the string containing atom index as key, and as value a list containing the unicode
        identifier of an emoji and whether it is colored or black emoji.

    Returns
    -------
    list
        List containing the svg text elements.

    """
    if '.svg' in name:
        fullname = directory + os.sep + name
    else:
        fullname = directory + os.sep + name + '.svg'

    svg = build_svg(mol, atom_radius=atom_radius, verbose=verbose, atom_color=atom_color,
                    radius_multi=radius_multi, thickness=thickness, shadow_light=shadow_light,
                    shadow=shadow, single_bonds=single_bonds, pos_multi=pos_multi, rotation=rotation, emoji=emoji)

    # Draw indices if emojis are present
    if emoji:
        for atom in mol.GetAtoms():
            atom.SetAtomMapNum(atom.GetIdx())
        rdMolDraw2D.MolDrawOptions.addAtomIndices = True
    if rdkit_png:
        rdkit.Chem.Draw.MolToFile(mol, directory + os.sep + name + "_rdkit.png")
    if rdkit_svg:
        drawer = rdMolDraw2D.MolDraw2DSVG(300, 300)
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        rdkit_svg_text = drawer.GetDrawingText()
        with open(directory + os.sep + name + "_rdkit.svg", 'w') as f:
            f.write(rdkit_svg_text)

    pdf_name = directory + os.sep + name + ".pdf"
    if save_pdf or save_png or save_jpeg:
        save_svg = True
        if save_png or save_jpeg:
            save_pdf = True
    if save_svg:
        svg_elementtree = ET.ElementTree(svg)
        ET.indent(svg_elementtree, space="\t", level=0)
        with open(fullname, 'wb') as f:
            svg_elementtree.write(f, encoding='utf-8')
    if save_pdf:
        drawing = svg2rlg(fullname)
        renderPDF.drawToFile(drawing, pdf_name)
    if save_png or save_jpeg:
        pages = convert_from_path(pdf_name)
    if save_png:
        pages[0].save(directory + os.sep + name + '.png', 'PNG')
    if save_jpeg:
        pages[0].save(directory + os.sep + name + '.jpeg', 'JPEG')

    print('\033[0;32m' + fullname + ' completed' + '\033[0;0;m')
    return svg


def graph_3d(mol, name='molecule_icon', directory=os.getcwd(), rdkit_png=False, rdkit_svg=False, resolution=100,
             atom_color=color_map, atom_radius=100, radius_multi=atom_resize, pos_multi=300,
             thickness=1 / 4, rotation=(0, 0, 0)):
    """This function takes a SMILES string and returns an icon of the molecule, in format PNG, SVG, JPEG, and PDF.

    Parameters
    ----------
    mol : mol object
        The rdkit mol object representing a molecule.
    name : string, default: 'molecule_icon'
        The name of the file to be saved.
    directory : string, default: os.getcwd()
        The directory to save the image in.
    rdkit_png : bool, optional
        If True, will use RDKit to generate a PNG image of the default structure.
    rdkit_svg : bool, optional
        If True, will use RDKit to generate an SVG image of the default structure.
    resolution : int, default: 100
        The resolution of the sphere and cylinder in the 3D graph.
    atom_color : dictionary, default: color_map
        a dictionary of atom colors. The keys are the atom symbols, and the values are the hex colors.
    atom_radius : int, default: 100
        The radius of the atoms in the icon.
    radius_multi : dictionary, default: atom_resize
        A dictionary containing the multiplier for each atom. It multiplies the atom radius.
    pos_multi : int, default: 300
        This is the distance between atoms.
    thickness : float, default: 1/4
        The thickness of the bonds compared to the atom radius.
    rotation : tuple, default: (0,0,0)
        Tuple containing the angle (in degree) of the x-axis, y-axis and z-axis to rotate the image.

    Returns
    -------
    plotly.graph_objects.Figure
        Plotly object containing the 3D structure of the molecule.

    """
    # produce rdkit image
    if rdkit_png:
        rdkit.Chem.Draw.MolToFile(mol, directory + os.sep + name + "_rdkit.png")
    if rdkit_svg:
        drawer = rdMolDraw2D.MolDraw2DSVG(300, 300)
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        rdkit_svg_text = drawer.GetDrawingText()
        with open(directory + os.sep + name + "_rdkit.svg", 'w') as f:
            f.write(rdkit_svg_text)

    conf = mol.GetConformer()
    max_radius_multi = atom_radius * max(radius_multi.values())
    pos_dict, max_pos, bond_map = position_map(mol, conf, rotation)
    # the dimension is calculated considering the maximum position, the atom diameter and multiplying by two (the
    # dimension is half of the image size)
    dimension = (max_pos * pos_multi + max_radius_multi * 2)
    # scale the position according to the image
    pos_dict = {k: val * pos_multi for k, val in pos_dict.items()}

    # create plotly graph with the white background
    layout = go.Layout(scene_xaxis_visible=False, scene_yaxis_visible=False, scene_zaxis_visible=False,
                       scene_aspectmode='cube')
    fig = go.Figure(layout=layout)

    # all_pos = np.array(list(pos_dict.values()))
    # x_cent, y_cent, z_cent = np.mean(all_pos[:, 0]), np.mean(all_pos[:, 1]), np.mean(all_pos[:, 2])
    # set equal axis dimension
    axis_range = [-dimension, dimension]
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=axis_range, ),
            yaxis=dict(range=axis_range, ),
            zaxis=dict(range=axis_range, ), ), )
    # build bonds
    for bond in mol.GetBonds():
        idx1 = bond.GetBeginAtomIdx()
        idx2 = bond.GetEndAtomIdx()
        color_scale = [[0, atom_color['Bond']], [1, atom_color['Bond']]]
        bond_thickness = int(atom_radius * thickness)
        name = f'{bond.GetIdx()}: {bond.GetBondType()}'
        (x_surf, y_surf, z_surf) = cylinder(bond_thickness, pos_dict[idx1], pos_dict[idx2], resolution=resolution)
        data = go.Surface(x=x_surf, y=y_surf, z=z_surf, colorscale=color_scale, name=name,
                          showscale=False, showlegend=False)
        fig.add_traces(data)

    # build atom icons
    for k, val in pos_dict.items():
        atom = mol.GetAtomWithIdx(k)
        symbol = atom.GetSymbol()
        radius = atom_radius * radius_multi[symbol]  # resize the atom dimension
        color_scale = [[0, atom_color[symbol]], [1, atom_color[symbol]]]
        name = f'{k}: {symbol}'
        (x_surf, y_surf, z_surf) = sphere(val[0], val[1], val[2], radius, resolution=resolution)
        data = go.Surface(x=x_surf, y=y_surf, z=z_surf, colorscale=color_scale, name=name,
                          showscale=False, showlegend=False)
        fig.add_traces(data)
    return fig


def parse():
    # create a parser for command line
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Produce 2D icons of molecules from smiles.')
    main = parser.add_argument_group('[ Required ]')
    main.add_argument('SMILE',
                      metavar='SMILE string',
                      help='Smile of the molecule to produce the icon')

    optional = parser.add_argument_group('[ Optional ]')
    optional.add_argument("--name",
                          metavar='STR',
                          default='molecule_icon',
                          help='Name of the png output file')
    optional.add_argument("-a", '--atom_multiplier',
                          metavar='FLOAT',
                          type=float,
                          default=1,
                          help='Increase or decrease the atom size in the image')
    optional.add_argument("-p", '--position_multiplier',
                          metavar='FLOAT',
                          type=float,
                          default=1,
                          help='Increase or decrease the image size in the image')
    optional.add_argument("-d", '--directory',
                          metavar='FOLDER',
                          default=os.getcwd(),
                          help='Path to the folder to save the icon file ')
    optional.add_argument("--rdkit_svg",
                          action='store_true',
                          help='Use this flag to save also the rdkit 2D image of the molecule')
    optional.add_argument("-s", "--single_bond",
                          action='store_true',
                          help='Use this flag to draw single bonds only')
    optional.add_argument("--remove_H",
                          action='store_true',
                          help='Use this flag to remove the hydrogens from the structure')
    optional.add_argument("--hide_shadows",
                          action='store_true',
                          help='Hide the shadows of the atoms')
    optional.add_argument('-t', "--thickness",
                          type=float,
                          default=0.35,
                          help='Line thickness compared to atom size, range [0:1]')
    optional.add_argument("--shadow_light",
                          type=float,
                          default=0.35,
                          help='Select how dark the shadow should be in the range [0:1]')
    optional.add_argument("-v", "--verbose",
                          action='store_true',
                          help='Print the 2D coordinates of each atom')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    parsed = parse()
    molecule = parse_structure(parsed.SMILE, remove_H=parsed.remove_H)
    icon_print(molecule, name=parsed.name, directory=parsed.directory, pos_multi=int(300 * parsed.position_multiplier),
               rdkit_svg=parsed.rdkit_svg, single_bonds=parsed.single_bond, save_png=True, verbose=parsed.verbose,
               atom_radius=100 * parsed.atom_multiplier, thickness=parsed.thickness,
               shadow=not parsed.hide_shadows, shadow_light=parsed.shadow_light)
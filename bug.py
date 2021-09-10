import copy
import gc
import os

import numpy as np
import torch
import transforms3d

from typing import List
from vispy import scene
from vispy.scene import visuals
from vispy.color import Color
from vispy.visuals.filters import Alpha
from vispy.io import write_png
from functools import reduce


def read_ply(mesh_fi):
    ply_fi = open(mesh_fi, 'r')
    Height = None
    Width = None
    hFov = None
    vFov = None
    num_vertex = -1
    while True:
        line = ply_fi.readline().split('\n')[0]
        if line.startswith('element vertex'):
            num_vertex = int(line.split(' ')[-1])
        elif line.startswith('element face'):
            num_face = int(line.split(' ')[-1])
        elif line.startswith('comment'):
            if line.split(' ')[1] == 'H':
                Height = int(line.split(' ')[-1].split('\n')[0])
            if line.split(' ')[1] == 'W':
                Width = int(line.split(' ')[-1].split('\n')[0])
            if line.split(' ')[1] == 'hFov':
                hFov = float(line.split(' ')[-1].split('\n')[0])
            if line.split(' ')[1] == 'vFov':
                vFov = float(line.split(' ')[-1].split('\n')[0])
        elif line.startswith('end_header'):
            break
    contents = ply_fi.readlines()
    vertex_infos = contents[:num_vertex]
    face_infos = contents[num_vertex:]
    verts = []
    colors = []
    faces = []
    for v_info in vertex_infos:
        str_info = [float(v) for v in v_info.split('\n')[0].split(' ')]
        if len(str_info) == 6:
            vx, vy, vz, r, g, b = str_info
        else:
            vx, vy, vz, r, g, b, hi = str_info
        verts.append([vx, vy, vz])
        colors.append([r, g, b, hi])
    verts = np.array(verts)
    try:
        colors = np.array(colors)
        colors[..., :3] = colors[..., :3] / 255.
    except:
        pass

    for f_info in face_infos:
        _, v1, v2, v3 = [int(f) for f in f_info.split('\n')[0].split(' ')]
        faces.append([v1, v2, v3])
    faces = np.array(faces)

    return verts, colors, faces, Height, Width, hFov, vFov


mesh_fi = 'mesh/output.ply'
verts, colors, faces, height, width, hfov, vfov = read_ply(mesh_fi)
import ipdb;ipdb.set_trace()

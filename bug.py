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


class CanvasView:
    def __init__(
        self,
        fov,
        verts,
        faces,
        colors,
        canvas: scene.SceneCanvas,
        view,
        mesh
    ):
        self.canvas = canvas
        self.view = view
        self.view.camera.fov = fov
        self.mesh = mesh
        self.tr = self.view.camera.transform
        self.mesh.set_data(
            vertices=verts,
            faces=faces,
            vertex_colors=colors[:, :3]
        )
        self.translate([0, 0, 0])
        self.rotate(axis=[1, 0, 0], angle=180)
        self.view_changed()

    def translate(self, trans=None):
        if trans is None:
            trans = [0, 0, 0]
        self.tr.translate(trans)

    def rotate(self, axis=None, angle=0):
        if axis is None:
            axis = [1, 0, 0]
        self.tr.rotate(axis=axis, angle=angle)

    def view_changed(self):
        self.view.camera.view_changed()

    def render(self):
        return self.canvas.render()

    def reinit_camera(self, fov):
        self.view.camera.fov = fov
        self.view.camera.view_changed()


class CanvasViewFactory:
    instance = None
    canvas = None
    view = None
    mesh = None

    @classmethod
    def new(
        cls,
        canvas_size,
        fov,
        verts,
        faces,
        colors
    ):
        if True or cls.canvas is None:
            cls.canvas = scene.SceneCanvas(
                bgcolor=Color('blue'),
                size=(canvas_size, canvas_size)
            )
            cls.view = cls.canvas.central_widget.add_view()
            cls.view.camera = 'perspective'
            cls.mesh = visuals.Mesh(shading=None)
            cls.mesh.attach(Alpha(1.0))
            cls.view.add(cls.mesh)

        return CanvasView(
            fov,
            verts,
            faces,
            colors,
            cls.canvas,
            cls.view,
            cls.mesh
        )


def output_3d_photo(
    verts,
    colors,
    faces,
    z_shift
):
    colors = colors[..., :3]

    canvas_size = 400

    fov = 60

    normal_canvas = CanvasViewFactory.new(
        canvas_size,
        fov,
        verts,
        faces,
        colors
    )

    img = normal_canvas.render()

    border = [0, img.shape[0], 0, img.shape[1]]

    img_h_len = 400
    anchor = [
        int(
            max(
                0,
                int((img.shape[0]) // 2 - img_h_len // 2)
            )
        ),
        int(
            min(
                int((img.shape[0]) // 2 + img_h_len // 2),
                (img.shape[0]) - 1
            )
        ),
        0,
        img.shape[1]
    ]

    anchor = np.array(anchor)
    ref_pose = np.eye(4)
    tgts_pose = ref_pose * 1.
    tgts_pose[:3, -1] = np.array([0., 0., z_shift])

    rel_pose = np.linalg.inv(np.dot(tgts_pose, np.linalg.inv(ref_pose)))
    axis, angle = transforms3d.axangles.mat2axangle(rel_pose[0:3, 0:3])
    normal_canvas.rotate(axis=axis, angle=(angle * 180) / np.pi)
    normal_canvas.translate(rel_pose[:3, 3])

    normal_canvas.reinit_camera(fov)

    normal_canvas.view_changed()
    img = normal_canvas.render()

    img = img[
      anchor[0]:anchor[1],
      anchor[2]:anchor[3]
    ]
    img = img[
      int(border[0]):int(border[1]),
      int(border[2]):int(border[3])
    ]

    path = 'tmp/output-%s.png' % z_shift
    print("mesh.py:", "Writing Inpainting output frame:", os.path.abspath(path))

    write_png(path, img)


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

for z_shift in range(0, 10):
    output_3d_photo(
        verts,
        colors,
        faces,
        z_shift * -0.1
    )

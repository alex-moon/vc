import gc
import os
from dataclasses import dataclass
from math import isclose, pi
from typing import List

import numpy as np
import transforms3d
from vispy import scene
from vispy.color import Color
from vispy.io import write_png
from vispy.scene import visuals
from vispy.visuals.filters import Alpha


@dataclass
class ImageSpec:
    texts: List[str] = None
    styles: List[str] = None
    iterations: int = 500
    init_iterations: int = None
    epochs: int = 1
    x_velocity: float = 0.
    y_velocity: float = 0.
    z_velocity: float = 0.
    upscale: bool = True


@dataclass
class VideoSpec:
    steps: List[ImageSpec]


@dataclass
class GenerationSpec:
    videos: List[VideoSpec] = None


class Acceleration:
    x = 0.0005
    y = 0.0005
    z = 0.0005


class Multiplier:
    x = -0.01
    y = 0.01
    z = -0.01

    @classmethod
    def accelerate_x(cls, x, target):
        target = cls.x * target
        if isclose(x, target, abs_tol=Acceleration.x * 0.5):
            return 0
        return Acceleration.x if x < target else -Acceleration.x

    @classmethod
    def accelerate_y(cls, y, target):
        target = cls.y * target
        if isclose(y, target, abs_tol=Acceleration.y * 0.5):
            return 0
        return Acceleration.y if y < target else -Acceleration.y

    @classmethod
    def accelerate_z(cls, z, target):
        target = cls.z * target
        if isclose(z, target, abs_tol=Acceleration.z * 0.5):
            return 0
        return Acceleration.z if z < target else -Acceleration.z


class Velocity:
    def __init__(self):
        self.x = 0.
        self.y = 0.
        self.z = 0.

    def accelerate(self, x_target, y_target, z_target):
        self.accelerate_x(x_target)
        self.accelerate_y(y_target)
        self.accelerate_z(z_target)

    def accelerate_x(self, target):
        self.x += Multiplier.accelerate_x(self.x, target)

    def accelerate_y(self, target):
        self.y += Multiplier.accelerate_y(self.y, target)

    def accelerate_z(self, target):
        self.z += Multiplier.accelerate_z(self.z, target)

    def to_tuple(self):
        return self.x, self.y, self.z

    def moving(self, x_target, y_target, z_target):
        x_result = self.x > 0 if x_target * Multiplier.x > 0 else self.x <= 0
        y_result = self.y > 0 if y_target * Multiplier.y > 0 else self.y <= 0
        z_result = self.z > 0 if z_target * Multiplier.z > 0 else self.z <= 0
        return x_result or y_result or z_result


class Translate:
    velocity: Velocity
    x_target: float
    y_target: float
    z_target: float
    x = 0.
    y = 0.
    z = 0.

    def __init__(
        self,
        x_target: float,
        y_target: float,
        z_target: float,
        previous=None
    ):
        self.x_target = x_target
        self.y_target = y_target
        self.z_target = z_target

        if previous is not None:
            self.velocity = previous.velocity
            self.x = previous.x
            self.y = previous.y
            self.z = previous.z
        else:
            self.velocity = Velocity()

    def move(self):
        self.velocity.accelerate(
            self.x_target,
            self.y_target,
            self.z_target
        )

        self.x += self.velocity.x
        self.y += self.velocity.y
        self.z += self.velocity.z

        return self.velocity.moving(
            self.x_target,
            self.y_target,
            self.z_target
        )

    def to_tuple(self):
        return self.x, self.y, self.z

    def reset(self):
        self.x = 0.
        self.y = 0.
        self.z = 0.


class GenerationRunner:
    @classmethod
    def iterate_steps(cls, spec: GenerationSpec):
        step = 0
        if spec.videos:
            for video in spec.videos:
                video_step = 0
                step += 1
                if video.steps:
                    for step_spec in video.steps:
                        if step_spec.texts:
                            for text in step_spec.texts:
                                if step_spec.styles:
                                    for style in step_spec.styles:
                                        for i in range(step_spec.epochs):
                                            video_step += 1
                                            step += 1
                                            yield step, video_step, step_spec
                                else:
                                    for i in range(step_spec.epochs):
                                        video_step += 1
                                        step += 1
                                        yield step, video_step, step_spec


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
        self.init(verts, faces, colors)

    def init(self, verts, faces, colors):
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
        result = self.canvas.render()
        return result

    def reinit_camera(self, fov):
        self.view.camera.fov = fov
        self.view.camera.view_changed()


class CanvasViewFactory:
    canvas = None
    view = None
    mesh = None

    @classmethod
    def new(
        cls,
        canvas_size,
        factor,
        fov,
        verts,
        faces,
        colors
    ):
        if cls.canvas is None:
            cls.canvas = scene.SceneCanvas  (
                bgcolor=Color('blue'),
                size=(canvas_size * factor, canvas_size * factor)
            )
            cls.mesh = visuals.Mesh(shading=None)
            cls.mesh.attach(Alpha(1.0))
        else:
            cls.view.parent = None
            del cls.view
            gc.collect()

        cls.view = cls.canvas.central_widget.add_view()
        cls.view.camera = 'perspective'
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
    i,
    translate_rotate,
):
    colors = colors[..., :3]

    canvas_size = 400
    init_factor = 1
    fov = 56.56
    # fov = 54

    normal_canvas = CanvasViewFactory.new(
        canvas_size,
        init_factor,
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
    # tgts_pose = ref_pose * 1.
    # tgts_pose[:3, -1] = np.array(translate_rotate)
    tgts_pose = np.array(translate_rotate)

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

    # path = f'tmp/{i:04}.png'
    path = 'debug.png'
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

tx = 0
ty = 0
tz = 0

rm = 2 * pi / 360
ax = 0.
ay = 5.
az = 0.

pose = np.eye(4)
pose[0:3, 0:3] = transforms3d.euler.euler2mat(ax * rm, ay * rm, az * rm)
pose[:3, -1] = [tx * Multiplier.x, ty * Multiplier.y, tz * Multiplier.z]

output_3d_photo(
    verts,
    colors,
    faces,
    1,
    pose
)

# os.system(
#     ' '.join(
#         [
#             'ffmpeg -y -i "tmp/%04d.png"',
#             '-b:v 8M -c:v h264_nvenc -pix_fmt yuv420p -strict -2',
#             '-filter:v "minterpolate=\'mi_mode=mci:mc_mode=aobmc:vsbmc=1:fps=60\'"',
#             'tmp/result.mp4'
#         ]
#     )
# )

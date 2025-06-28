import sys
import pygame
import numpy as np
from main import Mesh  # wavefront loader
from atividade6 import build_transformation_matrix

SCREEN_SIZE = (800, 600)
BG_COLOR = (30, 30, 30)
LINE_COLOR = (200, 200, 200)
FPS = 60

class Viewport2D:
    def __init__(self, window, viewport):
        # window: (wxmin, wymin, wxmax, wymax) in world coords
        # viewport: (vxmin, vymin, vxmax, vymax) in screen coords
        self.window = window
        self.viewport = viewport

    def world_to_screen(self, x, y):
        wxmin, wymin, wxmax, wymax = self.window
        vxmin, vymin, vxmax, vymax = self.viewport
        sx = vxmin + (x - wxmin) * (vxmax - vxmin) / (wxmax - wxmin)
        sy = vymax - (y - wymin) * (vymax - vymin) / (wymax - wymin)
        return int(sx), int(sy)


class DisplayObject:
    def __init__(self, mesh: Mesh, face_index: int):
        self.mesh = mesh
        self.face = face_index
        # extract list of points as 2D world coords (ignore z)
        self.vertices = [v.coords[:2] for v in mesh.vertices.values()]
        # store original vertices for reset
        self.original = np.array(self.vertices)
        self.transform = np.identity(3)

    def apply_transform(self, matrix):
        self.transform = matrix @ self.transform

    def get_transformed_edges(self):
        # edges of face
        edges = self.mesh.edges_of_face(self.face)
        pts = []
        for start, end in edges:
            # Skip edges with None values
            if start is None or end is None:
                continue
            p0 = np.array([*self.vertices[start - 1], 1.0])  # indices are 1-based
            p1 = np.array([*self.vertices[end - 1], 1.0])
            tp0 = self.transform @ p0
            tp1 = self.transform @ p1
            pts.append((tp0[:2], tp1[:2]))
        return pts


class DisplayFile:
    def __init__(self):
        self.objects = []

    def add(self, obj: DisplayObject):
        self.objects.append(obj)

    def draw(self, surface, viewport: Viewport2D):
        for obj in self.objects:
            for p0, p1 in obj.get_transformed_edges():
                x0, y0 = viewport.world_to_screen(p0[0], p0[1])
                x1, y1 = viewport.world_to_screen(p1[0], p1[1])
                pygame.draw.line(surface, LINE_COLOR, (x0, y0), (x1, y1), 1)


class InteractiveSystem:
    def __init__(self, obj_file):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Sistema Gráfico Iterativo 2D")
        self.clock = pygame.time.Clock()

        # load mesh
        self.mesh = Mesh()
        self.mesh.load_obj(obj_file)

        # setup display file (one object per face for demo)
        self.display = DisplayFile()
        for f in self.mesh.faces:
            dobj = DisplayObject(self.mesh, f)
            self.display.add(dobj)

        # default window and viewport
        self.viewport = Viewport2D(
            window=(-10, -10, 10, 10), viewport=(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1])
        )

        self.running = True

    def run(self):
        selected = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_TAB:
                        selected = (selected + 1) % len(self.display.objects)
                    # translate selected object with arrows
                    elif event.key in (
                        pygame.K_UP,
                        pygame.K_DOWN,
                        pygame.K_LEFT,
                        pygame.K_RIGHT,
                    ):
                        dx = dy = 0
                        if event.key == pygame.K_UP:
                            dy = 1
                        if event.key == pygame.K_DOWN:
                            dy = -1
                        if event.key == pygame.K_LEFT:
                            dx = -1
                        if event.key == pygame.K_RIGHT:
                            dx = 1
                        mat = build_transformation_matrix(
                            [("translate", [dx, dy])], dimension=2
                        )
                        self.display.objects[selected].apply_transform(mat)
                    elif event.key == pygame.K_r:
                        mat = build_transformation_matrix([("rotate", 10)], dimension=2)
                        self.display.objects[selected].apply_transform(mat)
                    elif event.key == pygame.K_s:
                        mat = build_transformation_matrix(
                            [("scale", [1.1, 1.1])], dimension=2
                        )
                        self.display.objects[selected].apply_transform(mat)

            self.screen.fill(BG_COLOR)
            self.display.draw(self.screen, self.viewport)
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python graphics2d.py <arquivo.obj>")
    else:
        InteractiveSystem(sys.argv[1]).run()

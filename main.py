import sys
import pygame
import numpy as np
from mesh import Mesh  # wavefront loader
from atividade6 import build_transformation_matrix

SCREEN_SIZE = (800, 600)
BG_COLOR = (30, 30, 30)
LINE_COLOR = (200, 200, 200)
SELECTED_COLOR = (100, 255, 255)  # Color for the selected object
OBJECT_COLORS = [  # Colors for different objects
    (200, 200, 200),  # White (default)
    (255, 100, 100),  # Red
    (100, 255, 100),  # Green
    (100, 100, 255),  # Blue
    (255, 255, 100),  # Yellow
    (255, 100, 255),  # Magenta
    (100, 255, 255),  # Cyan
]
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
    def __init__(self, mesh: Mesh, name=""):
        self.mesh = mesh
        self.name = name  # Store object name (from filename)
        # extract list of points as 2D world coords (ignore z)
        self.vertices = [v.coords[:2] for v in mesh.vertices.values()]
        # store original vertices for reset
        self.original = np.array(self.vertices)
        self.transform = np.identity(3)
        # Create a set of all edges to ensure we draw boundary edges
        self.all_edges = set()
        self._compute_all_edges()

        # Calculate center of the object
        self._calculate_center()

    def _calculate_center(self):
        """Calculate the center of the object based on its vertices"""
        if not self.vertices:
            self.center = np.array([0.0, 0.0])
            return

        # Calculate average of all vertices
        vertices_array = np.array(self.vertices)
        self.center = np.mean(vertices_array, axis=0)

    def _compute_all_edges(self):
        """Precompute all edges in the mesh including boundary edges"""
        # For each face, add its edges to the set
        for face_index in self.mesh.faces:
            face = self.mesh.faces[face_index]
            he = face.half_edge
            start = he
            while True:
                # Get vertices of this edge (in correct order)
                v1 = he.next.vertex.index
                v2 = he.vertex.index
                # Add edge as a tuple (smaller index first for consistency)
                edge = (min(v1, v2), max(v1, v2))
                self.all_edges.add(edge)
                he = he.next
                if he == start:
                    break

    def apply_transform(self, matrix):
        self.transform = matrix @ self.transform

    def rotate_around_center(self, angle_deg):
        """Apply a rotation around the object's center"""
        # Get current center position after all transformations so far
        center_point = np.array([self.center[0], self.center[1], 1.0])
        transformed_center = self.transform @ center_point
        current_center = transformed_center[:2]

        # Step 1: Translate object so its center is at origin
        translate_to_origin = np.identity(3)
        translate_to_origin[0, 2] = -current_center[0]
        translate_to_origin[1, 2] = -current_center[1]

        # Step 2: Rotate
        angle_rad = np.radians(angle_deg)
        cos_val, sin_val = np.cos(angle_rad), np.sin(angle_rad)
        rotation_matrix = np.identity(3)
        rotation_matrix[0, 0] = cos_val
        rotation_matrix[0, 1] = -sin_val
        rotation_matrix[1, 0] = sin_val
        rotation_matrix[1, 1] = cos_val

        # Step 3: Translate back to original position
        translate_back = np.identity(3)
        translate_back[0, 2] = current_center[0]
        translate_back[1, 2] = current_center[1]

        # Combine transformations
        combined_transform = translate_back @ rotation_matrix @ translate_to_origin

        # Apply to object's transformation matrix
        self.transform = combined_transform @ self.transform

    def get_transformed_edges(self):
        pts = []

        # Process all unique edges (including boundary edges)
        for v1, v2 in self.all_edges:
            p0 = np.array([*self.vertices[v1 - 1], 1.0])  # indices are 1-based
            p1 = np.array([*self.vertices[v2 - 1], 1.0])
            tp0 = self.transform @ p0
            tp1 = self.transform @ p1
            pts.append((tp0[:2], tp1[:2]))

        return pts


class DisplayFile:
    def __init__(self):
        self.objects = []

    def add(self, obj: DisplayObject):
        self.objects.append(obj)

    def clear(self):
        self.objects.clear()

    def draw(self, surface, viewport: Viewport2D, selected=None):
        for i, obj in enumerate(self.objects):
            if selected is not None and i == selected:
                color = SELECTED_COLOR
            else:
                color = OBJECT_COLORS[i % len(OBJECT_COLORS)]

            for p0, p1 in obj.get_transformed_edges():
                x0, y0 = viewport.world_to_screen(p0[0], p0[1])
                x1, y1 = viewport.world_to_screen(p1[0], p1[1])
                pygame.draw.line(surface, color, (x0, y0), (x1, y1), 1)


class InteractiveSystem:
    def __init__(self, obj_files):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Sistema Gráfico Interativo 2D")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        # setup display file
        self.display = DisplayFile()

        # Load all mesh files
        for file_path in obj_files:
            mesh = Mesh()
            mesh.load_obj(file_path)
            # Extract filename without extension as the object name
            name = file_path.split("\\")[-1].split("/")[-1].split(".")[0]
            self.display.add(DisplayObject(mesh, name))

        # default window and viewport
        self.viewport = Viewport2D(
            window=(-10, -10, 10, 10), viewport=(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1])
        )

        self.running = True
        self.selected = 0 if self.display.objects else None

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    # Switch between objects with Tab
                    elif event.key == pygame.K_TAB:
                        if self.display.objects:
                            self.selected = (self.selected + 1) % len(
                                self.display.objects
                            )
                    # translate object with arrows
                    elif (
                        event.key
                        in (
                            pygame.K_UP,
                            pygame.K_DOWN,
                            pygame.K_LEFT,
                            pygame.K_RIGHT,
                        )
                        and self.selected is not None
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
                        self.display.objects[self.selected].apply_transform(mat)
                    # Rotate selected object around its center
                    elif event.key == pygame.K_r and self.selected is not None:
                        self.display.objects[self.selected].rotate_around_center(10)
                    # Scale selected object
                    elif event.key == pygame.K_s and self.selected is not None:
                        mat = build_transformation_matrix(
                            [("scale", [1.1, 1.1])], dimension=2
                        )
                        self.display.objects[self.selected].apply_transform(mat)
                    # Unscale selected object
                    elif event.key == pygame.K_d and self.selected is not None:
                        mat = build_transformation_matrix(
                            [("scale", [0.9, 0.9])], dimension=2
                        )
                        self.display.objects[self.selected].apply_transform(mat)
                    # Counter-rotate selected object around its center
                    elif event.key == pygame.K_f and self.selected is not None:
                        self.display.objects[self.selected].rotate_around_center(-10)

            # Draw background
            self.screen.fill(BG_COLOR)

            # Draw all objects
            self.display.draw(self.screen, self.viewport, self.selected)

            # Display UI information
            if self.selected is not None and self.display.objects:
                selected_obj = self.display.objects[self.selected]
                text = f"Selected: {selected_obj.name} ({self.selected + 1}/{len(self.display.objects)})"
                text_surface = self.font.render(text, True, (255, 255, 255))
                self.screen.blit(text_surface, (10, 10))

            # Display controls
            controls = "Controls: Tab=Switch Object, Arrows=Move, R/F=Rotate, S/D=Scale"
            controls_surface = self.font.render(controls, True, (180, 180, 180))
            self.screen.blit(controls_surface, (10, SCREEN_SIZE[1] - 30))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Uso: python 2d_system.py <arquivo1.obj> [arquivo2.obj] [arquivo3.obj] ..."
        )
    else:
        # Pass all command line arguments (OBJ files) to the InteractiveSystem
        InteractiveSystem(sys.argv[1:]).run()

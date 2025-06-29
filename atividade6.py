import numpy as np
from math import cos, sin, radians


def build_transformation_matrix(transformations, dimension=2):
    if dimension == 2:
        matrix = np.identity(3)
        for op in transformations:
            if op[0] == "translate":
                dx, dy = op[1]
                t = np.array([[1, 0, dx], [0, 1, dy], [0, 0, 1]])
            elif op[0] == "rotate":
                theta = radians(op[1])
                t = np.array(
                    [
                        [cos(theta), -sin(theta), 0],
                        [sin(theta), cos(theta), 0],
                        [0, 0, 1],
                    ]
                )
            elif op[0] == "scale":
                sx, sy = op[1]
                t = np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]])
            else:
                raise ValueError(f"Unknown operation: {op[0]}")
            matrix = (
                matrix @ t
            )  # aplica na ordem correta, operador @ faz a multiplicação de matrizes
        return matrix

    elif dimension == 3:
        matrix = np.identity(4)
        for op in transformations:
            if op[0] == "translate":
                dx, dy, dz = op[1]
                t = np.array(
                    [[1, 0, 0, dx], [0, 1, 0, dy], [0, 0, 1, dz], [0, 0, 0, 1]]
                )
            elif op[0] == "rotate_x":
                theta = radians(op[1])
                t = np.array(
                    [
                        [1, 0, 0, 0],
                        [0, cos(theta), -sin(theta), 0],
                        [0, sin(theta), cos(theta), 0],
                        [0, 0, 0, 1],
                    ]
                )
            elif op[0] == "rotate_y":
                theta = radians(op[1])
                t = np.array(
                    [
                        [cos(theta), 0, sin(theta), 0],
                        [0, 1, 0, 0],
                        [-sin(theta), 0, cos(theta), 0],
                        [0, 0, 0, 1],
                    ]
                )
            elif op[0] == "rotate_z":
                theta = radians(op[1])
                t = np.array(
                    [
                        [cos(theta), -sin(theta), 0, 0],
                        [sin(theta), cos(theta), 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1],
                    ]
                )
            elif op[0] == "scale":
                sx, sy, sz = op[1]
                t = np.array(
                    [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]]
                )
            else:
                raise ValueError(f"Operação Desconhecida: {op[0]}")
            matrix = matrix @ t
        return matrix

    else:
        raise ValueError("Dimensão da Matrix precisa ser 2x2 ou 3x3")


# 2D: translação (10, 20), rotação 30 graus, escala (2, 2)
transforms_2d = [("translate", [10, 20]), ("rotate", 30), ("scale", [2, 2])]
m2d = build_transformation_matrix(transforms_2d, dimension=2)
# print("Matriz 2D:\n", m2d)

# 3D: rotação em X, depois translação
transforms_3d = [("rotate_x", 45), ("translate", [5, 0, 2]), ("scale", [1, 2, 1])]
m3d = build_transformation_matrix(transforms_3d, dimension=3)
# print("Matriz 3D:\n", m3d)

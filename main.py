class Vertex:
    def __init__(self, index, coords):
        self.index = index
        self.coords = coords
        self.half_edge = None


class HalfEdge:
    def __init__(self):
        self.vertex = None  # destino
        self.opposite = None
        self.next = None
        self.face = None


class Face:
    def __init__(self, index):
        self.index = index
        self.half_edge = None


class Mesh:
    def __init__(self):
        self.vertices = {}  # index -> Vertex
        self.half_edges = []  # list of HalfEdge
        self.faces = {}  # index -> Face
        self.edge_map = {}  # (start, end) -> HalfEdge

    def load_obj(self, filename):
        with open(filename) as f:
            lines = f.readlines()

        vertex_idx = 1
        face_idx = 1

        for line in lines:
            if line.startswith("v "):
                parts = line.strip().split()
                x, y, z = map(float, parts[1:])
                self.vertices[vertex_idx] = Vertex(vertex_idx, (x, y, z))
                vertex_idx = vertex_idx + 1
            elif line.startswith("f "):
                parts = line.strip().split()[1:]
                indices = [int(p.split("/")[0]) for p in parts]
                face = Face(face_idx)
                self.faces[face_idx] = face
                face_idx = face_idx + 1
                self._add_face(indices, face)
        """
        print(self.vertices, "\n")  # index -> Vertex
        print(self.half_edges, "\n")  # list of HalfEdge
        print(self.faces, "\n")  # index -> Face
        print(self.edge_map, "\n")
        """

    def _add_face(self, indices, face):
        n = len(indices)
        prev_he = None
        first_he = None
        for i in range(n):
            start = indices[i]
            end = indices[(i + 1) % n]
            he = HalfEdge()
            he.vertex = self.vertices[end]
            he.face = face
            if prev_he:
                prev_he.next = he
            else:
                first_he = he
            key = (start, end)
            self.edge_map[key] = he
            self.half_edges.append(he)
            self.vertices[start].half_edge = he
            # link opposite if it exists
            opp_key = (end, start)
            if opp_key in self.edge_map:
                he.opposite = self.edge_map[opp_key]
                self.edge_map[opp_key].opposite = he
            prev_he = he
        prev_he.next = first_he
        face.half_edge = first_he

    def faces_sharing_vertex(self, v_index):
        faces = set()
        v = self.vertices[v_index]
        start = v.half_edge
        he = start
        while True:
            if he.face:
                faces.add(he.face.index)
            if he.opposite:
                he = he.opposite.next
                if he == start:
                    break
            else:
                break
        return faces

    def edges_sharing_vertex(self, v_index):
        edges = set()
        v = self.vertices[v_index]
        start = v.half_edge
        he = start
        while True:
            key = (
                (he.opposite.vertex.index, he.vertex.index)
                if he.opposite
                else (None, he.vertex.index)
            )
            edges.add(
                (he.vertex.index, he.opposite.vertex.index)
                if he.opposite
                else (None, he.vertex.index)
            )
            if he.opposite:
                he = he.opposite.next
                if he == start:
                    break
            else:
                break
        return edges

    def faces_sharing_edge(self, start, end):
        key = (start, end)
        opp_key = (end, start)
        result = []
        if key in self.edge_map:
            he = self.edge_map[key]
            result.append(he.face.index if he.face else None)
        if opp_key in self.edge_map:
            he = self.edge_map[opp_key]
            result.append(he.face.index if he.face else None)
        return list(filter(None, result))

    def edges_of_face(self, face_index):
        face = self.faces[face_index]
        edges = []
        he = face.half_edge
        start = he
        while True:
            edges.append(
                (he.opposite.vertex.index if he.opposite else None, he.vertex.index)
            )
            he = he.next
            if he == start:
                break
        return edges

    def adjacent_faces(self, face_index):
        face = self.faces[face_index]
        adj = set()
        he = face.half_edge
        start = he
        while True:
            if he.opposite and he.opposite.face:
                adj.add(he.opposite.face.index)
            he = he.next
            if he == start:
                break
        return adj


if __name__ == "__main__":
    mesh = Mesh()
    mesh.load_obj("modelo2.obj")

    while True:
        print("\nMenu:")
        print("1. Faces que compartilham um vértice")
        print("2. Arestas que compartilham um vértice")
        print("3. Faces que compartilham uma aresta")
        print("4. Arestas de uma face")
        print("5. Faces adjacentes a uma face")
        print("0. Sair")

        choice = input("Escolha: ")

        if choice == "1":
            idx = int(input("Índice do vértice: "))
            print(mesh.faces_sharing_vertex(idx))
        elif choice == "2":
            idx = int(input("Índice do vértice: "))
            print(mesh.edges_sharing_vertex(idx))
        elif choice == "3":
            a = int(input("Vértice A da aresta: "))
            b = int(input("Vértice B da aresta: "))
            print(mesh.faces_sharing_edge(a, b))
        elif choice == "4":
            f = int(input("Índice da face: "))
            print(mesh.edges_of_face(f))
        elif choice == "5":
            f = int(input("Índice da face: "))
            print(mesh.adjacent_faces(f))
        elif choice == "0":
            break
        else:
            print("Opção inválida.")

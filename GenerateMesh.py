import os
import gmsh
from ConfigManager import ConfigManager


class GenerateMesh:
    def __init__(self, config_file):
        self.config = ConfigManager(config_file)
        self.n = ConfigManager(config_file).get_n()
        self.sample = ConfigManager(config_file).get_sample()
        self.lc_parameter = ConfigManager(config_file).get_lc()
        self.dir_where_mesh_and_geo_are_created = ConfigManager(config_file).dir_where_mesh_and_geo_are_created()
        self.change_name_of_msh_file = ConfigManager(config_file).get_change_name_of_msh_file()
        self.new_name_of_mesh = ConfigManager(config_file).get_new_name_of_mesh()
        self.create_geo_file = ConfigManager(config_file).get_create_geo_file()
        self.change_name_of_geo_file = ConfigManager(config_file).get_change_name_of_geo_file()
        self.new_name_of_geo = ConfigManager(config_file).get_new_name_of_geo()

    def create_points_and_lines(self):
        gmsh.initialize()
        # setting of the MSG file version - for using Flow123d - 2.2 is needed
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
        gmsh.option.setNumber("General.Terminal", 0)

        # Creates points in 2D for the square geometry
        for i in range(self.n + 1):
            for j in range(self.n + 1):
                x = i
                y = j
                z = 0
                gmsh.model.geo.addPoint(x, y, z, self.lc_parameter, (j + 1) + i * (self.n + 1))

        # empty lists that will hold the indexes that are needed to define the boundary
        lines_on_left_boundary = []
        lines_on_right_boundary = []

        # Creates vertical lines in 2D for the square geometry
        for i in range(self.n + 1):
            for j in range(self.n):
                line_index = gmsh.model.geo.addLine(i * (self.n + 1) + j + 1, i * (self.n + 1) + j + 2)
                if i == 0:
                    lines_on_left_boundary.append(line_index)
                elif i == self.n:
                    lines_on_right_boundary.append(line_index)

        # empty lists that will hold the indexes that are needed to define the boundary
        lines_on_top_boundary = []
        lines_on_bottom_boundary = []

        # Creates horizontal lines in 2D for the square geometry
        for i in range(self.n):
            for j in range(self.n + 1):
                line_index = gmsh.model.geo.addLine(i * (self.n + 1) + j + 1, (i + 1) * (self.n + 1) + j + 1)
                if j == 0:
                    lines_on_bottom_boundary.append(line_index)
                elif j == self.n:
                    lines_on_top_boundary.append(line_index)

        return lines_on_left_boundary, lines_on_right_boundary, lines_on_top_boundary, lines_on_bottom_boundary

    # this method creates the surfaces within the 2D geometry and returns the surface indexes
    def create_surfaces(self):
        surface_indixes = {}
        for i in range(self.n):
            for j in range(self.n):
                # Define curve loop
                loop_index = gmsh.model.geo.addCurveLoop(
                    [j + 1 + i * self.n, j + 2 + i * (self.n + 1) + self.n * (self.n + 1), -(j + 1 + (i + 1) * self.n),
                     -(j + 1 + i * (self.n + 1) + self.n * (self.n + 1))])

                # Create plane surface
                surface_index = gmsh.model.geo.addPlaneSurface([loop_index])

                # Store surface index in dictionary
                surface_indixes[(i, j)] = surface_index
        return surface_indixes

    # this method generates a mesh for the sandwich model
    def generate_mesh_sandwich(self):
        surface_indices = self.create_surfaces()

        # empty lists that will hold the needed indexes for the specific surface planes
        region_A = []
        region_B = []
        for i in range(self.n):
            for j in range(self.n):
                surface_index = surface_indices[(i, j)]
                if self.n % 2 == 0:
                    if surface_index % 2 == 0:
                        region_A.append(surface_index)
                    else:
                        region_B.append(surface_index)
                else:
                    if i % 2 == 0:
                        if surface_index % 2 == 0:
                            region_B.append(surface_index)
                        else:
                            region_A.append(surface_index)
                    else:
                        if surface_index % 2 == 0:
                            region_A.append(surface_index)
                        else:
                            region_B.append(surface_index)
        return region_A, region_B

    # this method generates a mesh for the chessboard model
    def generate_mesh_chessboard(self):
        surface_indices = self.create_surfaces()

        # empty lists that will hold the needed indexes for the specific surface planes
        region_A = []
        region_B = []
        for i in range(self.n):
            for j in range(self.n):
                surface_index = surface_indices[(i, j)]
                if self.n % 2 == 0:
                    if i % 2 == 0:
                        if surface_index % 2 == 0:
                            region_A.append(surface_index)
                        else:
                            region_B.append(surface_index)
                    else:
                        if surface_index % 2 == 0:
                            region_B.append(surface_index)
                        else:
                            region_A.append(surface_index)
                elif self.n % 2 != 0:
                    if surface_index % 2 == 0:
                        region_B.append(surface_index)
                    else:
                        region_A.append(surface_index)
        return region_A, region_B

    # this method generates the mesh based on the sample
    def generate_mesh_based_on_sample(self):
        lines_on_left_boundary, lines_on_right_boundary, lines_on_top_boundary, lines_on_bottom_boundary = self.create_points_and_lines()
        if self.sample == "chessboard":
            region_A, region_B = self.generate_mesh_chessboard()
        elif self.sample == "sandwich":
            region_A, region_B = self.generate_mesh_sandwich()

        gmsh.model.geo.synchronize()
        gmsh.model.addPhysicalGroup(1, lines_on_left_boundary, name=".left_boundary")
        gmsh.model.addPhysicalGroup(1, lines_on_right_boundary, name=".right_boundary")
        gmsh.model.addPhysicalGroup(1, lines_on_top_boundary, name=".top_boundary")
        gmsh.model.addPhysicalGroup(1, lines_on_bottom_boundary, name=".bottom_boundary")
        gmsh.model.addPhysicalGroup(2, region_A, name="region_A")
        gmsh.model.addPhysicalGroup(2, region_B, name="region_B")

        # Generates mesh
        gmsh.model.mesh.generate(2)

        if self.change_name_of_msh_file == "yes":
            msh_file_path = os.path.join(self.dir_where_mesh_and_geo_are_created, self.new_name_of_mesh)
        else:
            msh_file_path = os.path.join(self.dir_where_mesh_and_geo_are_created, "generated_mesh.msh")

        if self.create_geo_file == "yes":
            if self.change_name_of_geo_file == "yes":
                geo_unrolled_file_path = os.path.join(self.dir_where_mesh_and_geo_are_created, self.new_name_of_geo)
            else:
                geo_unrolled_file_path = os.path.join(self.dir_where_mesh_and_geo_are_created, "generated_geo.geo_unrolled")
            gmsh.write(geo_unrolled_file_path)


        gmsh.write(msh_file_path)
        # CHECK IF FILE IS CREATED with 2.2
        # Reads the old contents of the original .msh file
        with open(msh_file_path, "r") as file:
            old_msh_contents = file.read()

        # Modifies the desired part of the contents - changes from ASCII 4 to ASCII 2
        new_msh_contents = old_msh_contents.replace("$MeshFormat\n4.1 0 8", "$MeshFormat\n2.2 0 8")

        # Writes the modified contents back to the file
        with open(msh_file_path, "w") as file:
            file.write(new_msh_contents)
        gmsh.finalize()

        return msh_file_path
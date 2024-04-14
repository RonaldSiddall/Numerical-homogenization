import shutil
import numpy as np
import os
import sympy as sp
from ConfigManager import ConfigManager
from ruamel.yaml import YAML
yaml = YAML()


class GenerateVtuFiles:
    def __init__(self, file_msh, config_file):
        self.mesh = file_msh
        self.file_msh = file_msh
        self.E1 = ConfigManager(config_file).get_E1()
        self.E2 = ConfigManager(config_file).get_E2()
        self.E3 = ConfigManager(config_file).get_E3()
        self.Y1 = ConfigManager(config_file).get_Y1()
        self.Y2 = ConfigManager(config_file).get_Y2()
        self.dir_where_yamls_are_created = ConfigManager(config_file).get_dir_where_yamls_are_created()
        self.absolute_path_to_yaml_template = ConfigManager(config_file).get_absolute_path_to_yaml_template()
        self.directory_where_vtus_are_created = ConfigManager(config_file).get_directory_where_vtus_are_created()
        self.change_names_of_computed_yamls = ConfigManager(config_file).get_change_names_of_computed_yamls()
        self.new_names_of_yamls = ConfigManager(config_file).get_new_names_of_yamls()
        self.change_names_of_computed_output_dirs = ConfigManager(config_file).get_change_names_of_computed_output_dirs()
        self.new_names_of_output_dirs = ConfigManager(config_file).get_new_names_of_output_dirs()
        self.change_names_of_computed_vtu_files = ConfigManager(config_file).get_change_names_of_computed_vtu_files()
        self.new_names_of_vtu_files = ConfigManager(config_file).get_new_names_of_vtu_files()

    # this method deletes all contents within some directory_path
    def delete_directory_contents(directory_path):
        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

    def compute_boundary_conditions_strings(self):
        x, y = sp.symbols("x, y")
        vector_xy = np.array([x, y])

        # np.dot is the dot product of matrix E1 and the vector_xy = [x, y]
        u1 = np.dot(self.E1, vector_xy)
        u2 = np.dot(self.E2, vector_xy)
        u3 = np.dot(self.E3, vector_xy)

        # the lines of code below transform the vectors (1D arrays) to strings in the needed format
        # example case for E1 = [[1, 0], [0, 0]]
        # => u1 = E1 dot [x, y] => u1 = [x 0] (an 1D array - vector)
        # this vector is changed to a string without the brackets (done by str(u1)[1:-1])
        # so we get the string "x 0", after that we replace the " " by ", ".
        # lastly we add a zero and the brackets so the final string format is [x, 0, 0]
        # in summary: vector [x 0] -> string [x, 0, 0]
        u1_s = "[" + str(u1)[1:-1].replace(" ", ",") + ",0" + "]"
        u2_s = "[" + str(u2)[1:-1].replace(" ", ",") + ",0" + "]"
        u3_s = "[" + str(u3)[1:-1].replace(" ", ",") + ",0" + "]"
        return u1_s, u2_s, u3_s

    # this method prepares the yamls that are then passed on to be simulated using Flow123d
    # the yamls are created by rewritting a template with the specific parameters the user chose
    def compute_yamls(self):
        vector_u = self.compute_boundary_conditions_strings()
        # checks if the user wants to specify the names of the yaml files or use the default
        if self.change_names_of_computed_yamls != "yes":
            names_files = ["results1.yaml", "results2.yaml", "results3.yaml"]
        else:
            names_files = self.new_names_of_yamls

        # Checks if the directory where yamls should be created exists, if not, creates it
        os.makedirs(self.dir_where_yamls_are_created, exist_ok=True)
        # Deletes all contents within the destination directory
        GenerateVtuFiles.delete_directory_contents(self.dir_where_yamls_are_created)

        for i in range(3):
            with open(self.absolute_path_to_yaml_template, "r") as file:
                data = yaml.load(file)
                data["problem"]["mesh"]["mesh_file"] = self.file_msh.replace("C:", "/C")
                data["problem"]["flow_equation"]["mechanics_equation"]["input_fields"][0]["young_modulus"] = self.Y1
                data["problem"]["flow_equation"]["mechanics_equation"]["input_fields"][1]["young_modulus"] = self.Y2
                data["problem"]["flow_equation"]["mechanics_equation"]["input_fields"][2]["bc_displacement"]["value"] = vector_u[i]

            yaml_path = os.path.join(self.dir_where_yamls_are_created, names_files[i])
            with open(yaml_path, "w") as file:
                yaml.dump(data, file)

            with open(yaml_path, "r") as file:
                content = file.read()
                content = content.replace("'" + vector_u[i] + "'", vector_u[i])

            with open(yaml_path, "w") as file:
                file.write(content)

    # this method runs each yaml created in the previous method into the simulator Flow123d
    # the outputs after the simulation of each file is then saved within a directory the user chose
    def compute_outputs_mechanics(self):
        self.compute_yamls()

        # the path has to be /C/, so that is the reason we replace C: with /C
        changed_directory = self.dir_where_yamls_are_created.replace("C:", "/C")
        # checks if the user wants to specify the names of the output directories or use the default

        if self.change_names_of_computed_output_dirs == "yes":
            output_dirs = self.new_names_of_output_dirs
        else:
            output_dirs = ["output1", "output2", "output3"]

        for i, yaml_file in enumerate(os.listdir(self.dir_where_yamls_are_created)):
            output_dir = output_dirs[i]
            yaml_path = os.path.join(changed_directory, yaml_file).replace("\\", "/")
            output_path = os.path.join(changed_directory, output_dir).replace("\\", "/")

            # this command runs the simulator flow123d
            # -s -- solves for given yaml_path
            # -o -- defines the output_path where the results should be saved
            # > NUL 2>&1 - When flow123d runs it outputs a message with a lot of information
            # by using > NUL 2>&1 we choose not to display this message after running the command
            command = f"flow123d -s {yaml_path} -o {output_path} > NUL 2>&1"
            os.system(command)

            # this is to ensure that the indexes do not overflow
            if i == 2:
                break

    def compute_vtu_files(self):
        self.compute_outputs_mechanics()
        extracted_files = []
        if self.change_names_of_computed_output_dirs == "yes":
            names_outputs = self.new_names_of_output_dirs
        else:
            names_outputs = ["output1", "output2", "output3"]
        output_dirs = [
            self.dir_where_yamls_are_created + "/" + names_outputs[0],
            self.dir_where_yamls_are_created + "/" + names_outputs[1],
            self.dir_where_yamls_are_created + "/" + names_outputs[2],]

        # Checks if the directory where vtus should be created exists, if not, creates it
        os.makedirs(self.directory_where_vtus_are_created, exist_ok=True)

        # Deletes all contents within the destination directory
        GenerateVtuFiles.delete_directory_contents(self.directory_where_vtus_are_created)
        # checks if the user wants to specify the names of the vtu files or use the default
        if self.change_names_of_computed_vtu_files == "yes":
            new_vtu_file_names = self.new_names_of_vtu_files
        else:
            new_vtu_file_names = [f"{i}_mechanics-00000.vtu" for i in range(1, len(output_dirs) + 1)]

        for i, output_dir in enumerate(output_dirs, 1):
            vtu_file_path = os.path.join(output_dir, "mechanics", "mechanics-000000.vtu")

            # constructs a new file name
            new_filename = f"{new_vtu_file_names[i - 1]}"

            # copies the vtu file from the original dir to the destination with the new filename
            shutil.copy(vtu_file_path, os.path.join(self.directory_where_vtus_are_created, new_filename),)

            # adds the path to the extracted vtu file to the list of extracted files
            extracted_files.append(os.path.join(self.directory_where_vtus_are_created, new_filename).replace("\\", "/"))

        return extracted_files

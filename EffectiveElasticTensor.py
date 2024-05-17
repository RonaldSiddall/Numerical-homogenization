import os
import shutil

import numpy as np
import pyvista as pv
from GenerateVtuFiles import GenerateVtuFiles
from ConfigManager import ConfigManager


def delete_directory(directory_path, decider_deletion):
    if decider_deletion == "yes":
        try:
            # Attempts to delete the directory
            shutil.rmtree(directory_path)
            # Prints a message if deletion is successful
            print(f"\n  - Directory '{directory_path}' was deleted after the computation")
        except Exception as e:
            # Prints an error message if deletion fails
            print(f"Error deleting directory '{directory_path}': {e}")


class EffectiveElasticTensor:
    def __init__(self, file_msh, config_file):
        self.n = ConfigManager(config_file).get_n()
        self.sample = ConfigManager(config_file).get_sample()
        self.Y1 = ConfigManager(config_file).get_Y1()
        self.Y2 = ConfigManager(config_file).get_Y2()
        self.name_of_file_with_tensor = ConfigManager(config_file).get_name_of_file_with_tensor()
        self.output_dir_of_file_with_tensor = ConfigManager(config_file).get_output_dir_of_file_with_tensor()
        self.delete_yaml_dir_after_simulation = ConfigManager(config_file).get_delete_yaml_dir_after_simulation()
        self.delete_vtu_dir_after_simulation = ConfigManager(config_file).get_delete_vtu_dir_after_simulation()
        self.dir_where_yamls_are_created = ConfigManager(config_file).get_dir_where_yamls_are_created()
        self.directory_where_vtus_are_created = ConfigManager(config_file).get_directory_where_vtus_are_created()
        self.vtu_dirs = GenerateVtuFiles(file_msh, config_file).extract_vtu_files()
        self.meshes = []
        for vtu_file in self.vtu_dirs:
            self.meshes.append(pv.UnstructuredGrid(vtu_file))

    def compute_sigmas(self):
        sigmas = []
        for mesh in self.meshes:
            sigmas.append(mesh.cell_data.get("stress"))
        return sigmas

    def compute_meshes_with_areas(self):
        mesh_with_areas = []
        for mesh in self.meshes:
            mesh_with_areas.append(mesh.compute_cell_sizes(area=True).get_array("Area"))
        return mesh_with_areas

    def compute_effect_elast_constants_voigt(self):
        constants_voigt_list = []
        sigmas = self.compute_sigmas()
        areas = self.compute_meshes_with_areas()
        amount_of_meshes = len(self.meshes)

        for i in range(amount_of_meshes):
            sigma = sigmas[i]
            area = areas[i]
            stress_area = []
            for j in range(len(sigma)):
                stress_area.append(sigma[j, :] * area[j])

            all_constants = np.sum(stress_area, axis=0) / np.sum(area)
            # all_constants: for each load case we get a matrix 3x3 so in total there
            # are 3 matrices with 9 constants => 27 constants
            # in each individual matrix has this form:
            # [a b  0
            #  b c  0
            #  0 0  0]
            # where a, b, c are the effective elastic coefficients
            # because we don't care about zeros in this matrix, so we need to only extract a, b, c
            # that is the reason for the indexes 0, 1, 4 = index 0 - a, index 1 - b, index 4 - c
            needed_indexes = [0, 4, 1]
            # if we look at the 2x2 matrix [a b , b c] then in voigt notation we get [a, b, c]
            # and this vector [a, b, c] for the first load case = first column in the final tensor
            # second case: second column
            # third case: third column
            constants_voigt = [all_constants[index] for index in needed_indexes]
            constants_voigt_list.append(constants_voigt)
        return constants_voigt_list

    def get_tensor_in_txt_formatted(self):
        coefficients = self.compute_effect_elast_constants_voigt()
        os.makedirs(self.output_dir_of_file_with_tensor, exist_ok=True)
        GenerateVtuFiles.delete_directory_contents(self.output_dir_of_file_with_tensor)
        file_path = (self.output_dir_of_file_with_tensor + "/" + self.name_of_file_with_tensor + ".txt")
        # the {coefficients[2][0]}, {coefficients[2][1]}, {coefficients[2][2]} need to be divided by two
        # the reason is written in the theory
        with open(file_path, "w") as txt_file:
            txt_file.write("Settings of the simulation:\n")
            txt_file.write(f" - n: {self.n}\n")
            txt_file.write(f" - Type of geometry: {self.sample}\n")
            txt_file.write(f" - Y1: {self.Y1}\n")
            txt_file.write(f" - Y2: {self.Y2}\n")
            txt_file.write(
                "============================================================================================\n")
            txt_file.write("                    Effective elastic tensor in matrix form for 2D problems\n")
            txt_file.write(
                "============================================================================================\n\n")
            txt_file.write(
                f"            {coefficients[0][0]}           {coefficients[1][0]}      {coefficients[2][0] / 2}\n")
            txt_file.write(
                f"C =         {coefficients[0][1]}         {coefficients[1][1]}       {coefficients[2][1] / 2}\n")
            txt_file.write(
                f"            {coefficients[0][2]}          {coefficients[1][2]}      {coefficients[2][2] / 2}\n\n\n")
            txt_file.write(
                "--------------------------------------------------------------------------------------------\n")
            txt_file.write("This result was computed using these files:\n")
            for vtu_file in self.vtu_dirs:
                txt_file.write(f"{vtu_file}\n")

        delete_directory(self.dir_where_yamls_are_created, self.delete_yaml_dir_after_simulation)
        delete_directory(self.directory_where_vtus_are_created, self.delete_vtu_dir_after_simulation)

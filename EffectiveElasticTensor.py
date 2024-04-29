import os
import shutil

import numpy as np
import pyvista as pv
from GenerateVtuFiles import GenerateVtuFiles
from ConfigManager import ConfigManager


def delete_directory(directory_path, decider_deletion):
    if decider_deletion == "yes":
        try:
            # Attempt to delete the directory
            shutil.rmtree(directory_path)
            # Print a message if deletion is successful
            print(f"\n  - Directory '{directory_path}' was deleted after the computation")
        except Exception as e:
            # Print an error message if deletion fails
            print(f"Error deleting directory '{directory_path}': {e}")


class EffectiveElasticTensor:
    def __init__(self, file_msh, config_file):
        self.n = ConfigManager(config_file).get_n()
        self.sample = ConfigManager(config_file).get_sample()
        self.Y1 = ConfigManager(config_file).get_Y1()
        self.Y2 = ConfigManager(config_file).get_Y2()
        self.name_of_file_with_tensor = ConfigManager(config_file).get_name_of_file_with_tensor()
        self.output_dir_of_file_with_tensor = ConfigManager(config_file).get_output_dir_of_file_with_tensor()
        self.want_to_display_visualisation = ConfigManager(config_file).get_want_to_display_visualisation()
        self.what_to_display = ConfigManager(config_file).get_what_to_display()
        self.delete_yaml_dir_after_simulation = ConfigManager(config_file).get_delete_yaml_dir_after_simulation()
        self.delete_vtu_dir_after_simulation = ConfigManager(config_file).get_delete_vtu_dir_after_simulation()
        self.dir_where_yamls_are_created = ConfigManager(config_file).get_dir_where_yamls_are_created()
        self.directory_where_vtus_are_created = ConfigManager(config_file).get_directory_where_vtus_are_created()
        self.vtu_dirs = GenerateVtuFiles(file_msh, config_file).compute_vtu_files()
        self.meshes = []
        for vtu_file in self.vtu_dirs:
            self.meshes.append(pv.UnstructuredGrid(vtu_file))

    def get_source_files(self):
        return self.vtu_dirs

    def compute_meshes(self):
        return self.meshes

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

    def compute_multiplied_area_stresses(self):
        multiplied_area_stresses = []
        for mesh, sigma, area in zip(self.meshes, self.compute_sigmas(), self.compute_meshes_with_areas()):
            stress_area = []
            for i in range(len(sigma)):
                stress_area.append(sigma[i, :] * area[i])
            multiplied_area_stresses.append(stress_area)
        return multiplied_area_stresses

    def compute_mean_stresses(self):
        mean_stresses = []
        for stress in self.compute_multiplied_area_stresses():
            mean_stresses.append(np.mean(stress, axis=0))
        return mean_stresses

    def compute_sum_areas_of_all_elements(self):
        sum_areas = []
        for area in self.compute_meshes_with_areas():
            sum_areas.append(np.sum(area))
        return sum_areas

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
            needed_indexes = [0, 4, 1]
            constants_voigt = [all_constants[index] for index in needed_indexes]
            constants_voigt_list.append(constants_voigt)
        return constants_voigt_list

    def compute_reduced_voigt_vector(self):
        self.compute_effect_elast_constants_voigt()

    def visualize_all_vtu_files(self):
        if self.want_to_display_visualisation.lower() == "yes":
            for mesh in self.meshes:
                mesh.cell_data.get(self.what_to_display)
                mesh.plot(scalars=self.what_to_display)

    def get_tensor_in_txt_formatted(self):
        self.visualize_all_vtu_files()
        coefficients = self.compute_effect_elast_constants_voigt()
        os.makedirs(self.output_dir_of_file_with_tensor, exist_ok=True)
        GenerateVtuFiles.delete_directory_contents(self.output_dir_of_file_with_tensor)
        file_path = (self.output_dir_of_file_with_tensor + "/" + self.name_of_file_with_tensor + ".txt")
        # the {coefficients[2][0]}, {coefficients[2][1]}, {coefficients[2][2]} need to be divided by two
        # the reason is written in the theory
        with open(file_path, "w") as txt_file:
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

    def write_constants_to_file(self, output_path):
        coefficients = self.compute_effect_elast_constants_voigt()
        with open(output_path, 'a') as file:
            file.write("\n-----------------------------------------------------------------------------\n")
            file.write(f"Results for {self.sample}, n = {self.n}, Y1 = {self.Y1}, Y2 = {self.Y2}\n")
            file.write(f"{coefficients[0][0]}\n")
            file.write(f"{coefficients[1][1]}\n")
            file.write(f"{coefficients[2][2] / 2}\n")
            file.write(f"{coefficients[2][1] / 2}\n")
            file.write(f"{coefficients[2][0] / 2}\n")
            file.write(f"{coefficients[1][0]}\n")


        delete_directory(self.dir_where_yamls_are_created, self.delete_yaml_dir_after_simulation)
        delete_directory(self.directory_where_vtus_are_created, self.delete_vtu_dir_after_simulation)

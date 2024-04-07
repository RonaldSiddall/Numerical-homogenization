import numpy as np
import pyvista as pv


class EffectiveElasticTensor:

    def __init__(self, vtu_dirs):
        self.vtu_dirs = vtu_dirs
        self.meshes = []
        for vtu_file in vtu_dirs:
            self.meshes.append(pv.UnstructuredGrid(vtu_file))

    def get_source_files(self):
        return self.vtu_dirs

    def get_meshes(self):
        return self.meshes

    def get_sigmas(self):
        sigmas = []
        for mesh in self.meshes:
            sigmas.append(mesh.cell_data.get("stress"))
        return sigmas

    def get_meshes_with_areas(self):
        mesh_with_areas = []
        for mesh in self.meshes:
            mesh_with_areas.append(mesh.compute_cell_sizes(area=True).get_array("Area"))
        return mesh_with_areas

    def get_multiplied_area_stresses(self):
        multiplied_area_stresses = []
        for mesh, sigma, area in zip(self.meshes, self.get_sigmas(), self.get_meshes_with_areas()):
            stress_area = []
            for i in range(len(sigma)):
                stress_area.append(sigma[i, :] * area[i])
            multiplied_area_stresses.append(stress_area)
        return multiplied_area_stresses

    def get_mean_stresses(self):
        mean_stresses = []
        for stress in self.get_multiplied_area_stresses():
            mean_stresses.append(np.mean(stress, axis=0))
        return mean_stresses

    def get_sum_areas_of_all_elements(self):
        sum_areas = []
        for area in self.get_meshes_with_areas():
            sum_areas.append(np.sum(area))
        return sum_areas

    def get_effect_elast_constants_voigt(self):
        constants_voigt_list = []
        sigmas = self.get_sigmas()
        areas = self.get_meshes_with_areas()
        amount_of_meshes = len(self.meshes)
        stress_area = []

        for i in range(amount_of_meshes):
            sigma = sigmas[i]
            area = areas[i]
            for j in range(len(sigma)):
                stress_area.append(sigma[j, :] * area[j])

            all_constants = np.sum(stress_area, axis=0) / np.sum(area)

            # Select needed indexes
            needed_indexes = [0, 4, 1]

            # Extract constants corresponding to needed indexes
            constants_voigt = [all_constants[index] for index in needed_indexes]
            constants_voigt_list.append(constants_voigt)

        return constants_voigt_list

    def visualize_all_vtu_files(self, what_display):
        for mesh in self.meshes:
            mesh.cell_data.get(what_display)
            mesh.plot(scalars=what_display)

    def get_tensor_in_txt(self, name_of_file, output_file_path):
        coefficients = self.get_effect_elast_constants_voigt()
        file_path = output_file_path + name_of_file + ".txt"
        with open(file_path, "w") as txt_file:
            txt_file.write("============================================================================================\n")
            txt_file.write("                    Effective elastic tensor in matrix form for 2D problems\n")
            txt_file.write("============================================================================================\n\n")
            txt_file.write(f"            {coefficients[0][0]}           {coefficients[1][0]}      {coefficients[2][0] / 2}\n")
            txt_file.write(f"C =         {coefficients[0][1]}         {coefficients[1][1]}       {coefficients[2][1] / 2}\n")
            txt_file.write(f"            {coefficients[0][2]}          {coefficients[1][2]}      {coefficients[2][2] / 2}\n\n\n")
            txt_file.write("--------------------------------------------------------------------------------------------\n")
            txt_file.write("This result was computed with these files:\n")
            for vtu_file in self.vtu_dirs:
                txt_file.write(f"{vtu_file}\n")
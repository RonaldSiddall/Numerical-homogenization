import numpy as np
import pyvista as pv


def compute_average_stress_all(vtu_file_dir):
    mesh = pv.UnstructuredGrid(vtu_file_dir)
    sigma = mesh.cell_data.get("stress")

    # Average of each column of sigma (axis=0 is for averaging columns, axis=1 for rows)
    column_averages = np.mean(sigma, axis=0)

    # An empty list to store the values of the column averages
    results = []

    # Append each value into the empty list
    for value in column_averages:
        results.append(value)
    return results


def compute_stress_voigt_form(vtu_file_dir):
    results = compute_average_stress_all(vtu_file_dir)

    # remaining indexes have values 0, so no need to include them
    needed_indexes = [0, 4, 1]
    voigt_vector = []
    for i in needed_indexes:
        new_value = results[i]
        voigt_vector.append(new_value)
    return voigt_vector


def compute_coefficients_effective_elastic_tensor(vtu_file_dirs):
    coefficients = []
    for vtu_file in vtu_file_dirs:
        average_stress = compute_stress_voigt_form(vtu_file)
        coefficients.append(average_stress)
    return coefficients


def visualize_vtu_file_(vtu_file, what_display):
    mesh = pv.UnstructuredGrid(vtu_file)
    mesh.cell_data.get(what_display)
    mesh.plot(scalars=what_display)


def visualize_all_vtu_files(vtu_dirs, what_display):
    for vtu_file in vtu_dirs:
        visualize_vtu_file_(vtu_file, what_display)

import numpy as np
import pyvista as pv


# this method computes the areas of every element in a vtu file
def compute_area_of_elements_one_file(vtu_file):
    mesh = pv.UnstructuredGrid(vtu_file)

    # Computes cell sizes of areas for the mesh
    mesh_with_areas = mesh.compute_cell_sizes(area=True)

    # The result is a 1D matrix - array with areas of the elements
    area = mesh_with_areas.get_array("Area")
    return area


# this method extracts the stress, then returns the raw values in a 2D array
def compute_stress_one_file(vtu_file_dir):
    mesh = pv.UnstructuredGrid(vtu_file_dir)
    sigma = mesh.cell_data.get("stress")
    return sigma


# this method multiplies the area of each element with the 9 stresses that are in that element
# returns the resulting stress, that was gained by multiplying
def compute_multiplied_area_stress_one_file(vtu_file_dir):
    stress = compute_stress_one_file(vtu_file_dir)
    area = compute_area_of_elements_one_file(vtu_file_dir)
    indexes_stress = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    for i in range(len(stress)):
        for j in indexes_stress:
            stress[i][j] = stress[i][j] * area[i]
    return stress


# this method computes the mean of the above method, returns the mean of each stress
# in other words the results are the means of the corresponding stresses in that column
def compute_mean_stress_one_file(vtu_file_dir):
    stress = compute_multiplied_area_stress_one_file(vtu_file_dir)

    # axis=0 - computes the mean of that specific column, axis=1 computes mean of row
    stress_averages = np.mean(stress, axis=0)
    return stress_averages


# this method sums up the areas of each element, then returns it
def compute_sum_area_of_all_elements(vtu_file_dir):
    area = compute_area_of_elements_one_file(vtu_file_dir)
    sum_area = area.sum()
    return sum_area


# this method finds the total amount of elements within a mesh
def compute_amount_of_elements(vtu_file_dir):
    mesh = pv.UnstructuredGrid(vtu_file_dir)
    amount_elements = mesh.number_of_cells
    return amount_elements


# this method computes the effective constants by multiplying the stress by the amount of elements
# and dividing by the total area of the whole geometry (the same as the sum of areas of all elements)
def compute_effect_elast_constants_one_file(vtu_file_dir):
    amount_elements = compute_amount_of_elements(vtu_file_dir)
    total_area = compute_sum_area_of_all_elements(vtu_file_dir)
    stress = compute_mean_stress_one_file(vtu_file_dir)
    constants = []
    for i in range(len(stress)):
        constants.append(stress[i] * amount_elements / total_area)
    return constants


# this method takes the above method and does not include the stresses, that have a value of 0
# the stresses that have a 0 value are predetermined, so it is possible to exclude them easily
def compute_final_constants_voigt_form(vtu_file_dir):
    constants = compute_effect_elast_constants_one_file(vtu_file_dir)
    needed_indexes = [0, 4, 1]
    constants_voigt = []
    for needed_index in needed_indexes:
        constants_voigt.append(constants[needed_index])
    return constants_voigt


"""""
Maybe try this variant to take make a general method to intake a function?
Just an idea on how to make a generalised method and how to improve the code structure

def compute_some_function_for_more_files(functions, vtu_dirs):
    results = []
    for function in functions:
        for vtu_file in vtu_dirs:
            results.append(function(vtu_file))
    return results
    
    I understand this method would not work in this form, but perhaps worth thinking about?
"""

""""
From this point forward, all the above methods are used again, but for more data files.
In other words the methods below compute the complete effective elastic tensor 
by using the above methods on all the data files. They do so at the same time.

"""


# does the same but more vtu files
def compute_areas_more_files(vtu_dirs):
    # The areas are saved in a 2D matrix - array
    areas = []
    for vtu_file in vtu_dirs:
        areas.append(compute_area_of_elements_one_file(vtu_file))
    return areas


# does the same but for more files
def compute_stress_more_files(vtu_dirs):
    sigmas = []
    for vtu_file in vtu_dirs:
        sigmas.append(compute_stress_one_file(vtu_file))
    return sigmas


# does the same but for more vtu files
def compute_multiplied_area_stress_more_files(vtu_dirs):
    stresses = []
    for vtu_file in vtu_dirs:
        stresses.append(compute_multiplied_area_stress_one_file(vtu_file))
    return stresses


# does the same but for more vtu files
def compute_average_stress_more_files(vtu_dirs):
    stresses_averages = []
    for vtu_file in vtu_dirs:
        stresses_averages.append(compute_mean_stress_one_file(vtu_file))
    return stresses_averages


# does the same but for more vtu files
def compute_sum_area_of_all_elements_more_files(vtu_dirs):
    sums_areas = []
    for vtu_file in vtu_dirs:
        sums_areas.append(compute_sum_area_of_all_elements(vtu_file))
    return sums_areas


# does the same but for more vtu files
def compute_amount_of_elements_more_files(vtu_dirs):
    amounts_elements = []
    for vtu_file in vtu_dirs:
        amounts_elements.append(compute_amount_of_elements(vtu_file))
    return amounts_elements


# does the same but for more vtu files
def compute_effect_elast_constants_more_files(vtu_dirs):
    constants_more_files = []
    for vtu_file in vtu_dirs:
        constants_more_files.append(compute_effect_elast_constants_one_file(vtu_file))
    return constants_more_files


# does the same but for more vtu files
def compute_final_constants_voigt_form_whole_tensor(vtu_dirs):
    effective_elastic_tensor_constants = []
    for vtu_file in vtu_dirs:
        effective_elastic_tensor_constants.append(compute_final_constants_voigt_form(vtu_file))
    return effective_elastic_tensor_constants

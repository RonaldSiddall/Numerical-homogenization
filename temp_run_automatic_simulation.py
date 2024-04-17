import sys

from time import gmtime, strftime
import numpy as np
import yaml
import os
from EffectiveElasticTensor import EffectiveElasticTensor
from GenerateMesh import GenerateMesh
from ConfigManager import ConfigManager

def modify_n_in_config(config_file, new_n):
    # Load the YAML configuration file
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    # Modify the value of n
    config["simulation_parameters"]["n"] = new_n

    # Write the modified configuration back to a temporary YAML file
    temp_config_file = config_file.replace(".yaml", "_temp.yaml")
    with open(temp_config_file, 'w') as file:
        yaml.dump(config, file)

    return temp_config_file


def simulate_autopilot(config_file, start_n, end_n, step):
    for n in range(start_n, end_n + 1, step):
        # Create a modified copy of the original config file for this simulation run
        temp_config_file = modify_n_in_config(config_file, n)

        # Generate mesh and compute elastic tensor using the modified config
        file_msh = GenerateMesh(temp_config_file).generate_mesh_based_on_sample()

        EffectiveElasticTensor(file_msh, temp_config_file).write_constants_to_file(start_n,end_n,step)

        # Remove the temporary config file after use
        os.remove(temp_config_file)
        print(f"Simulation {n} completed")


def get_only_unique_constants(config_file, n_new):
    temp_config_file = modify_n_in_config(config_file, n_new)
    file_msh = GenerateMesh(temp_config_file).generate_mesh_based_on_sample()
    all_constants = EffectiveElasticTensor(file_msh, temp_config_file).compute_effect_elast_constants_voigt()

    # unique constants - voigt notation of the effective elastic tensor
    unique_constants = [[
        all_constants[0][0],
        all_constants[1][1],
        all_constants[2][2] / 2,
        all_constants[1][2],
        all_constants[0][2],
        all_constants[0][1]
    ]]
    os.remove(temp_config_file)
    return unique_constants


def compute_difference_constants(config_file, start_n, end_n, step, output_file, tolerance):
    config_manager = ConfigManager(config_file)
    Y1 = config_manager.get_Y1()
    Y2 = config_manager.get_Y2()
    sample = ConfigManager(config_file).get_sample()
    total_iterations = (end_n - start_n) // step
    results = []
    i = 1
    for n_new in range(start_n + 1, end_n + 1, step):
        if n_new == start_n+1:
            print("==================================")
            print("THE AUTOMATIC SIMULATION STARTED")
            print("==================================")
            print("Settings of the simulation:")
            print(f" - Type of geometry: {sample}")
            print(f" - Y1: {Y1}")
            print(f" - Y2: {Y2}")
            print(f" - n: {start_n} to {end_n}")
            print(f" - step: {step}")
            print(f" - tolerance: {tolerance}")
            print(f" - output: {output_file}")
            print("-----------------------------------")
            print("Progress status of the simulation:")
            print("-----------------------------------")
        n_old = n_new - 1
        old_coef = np.array(get_only_unique_constants(config_file, n_old))
        new_coef = np.array(get_only_unique_constants(config_file, n_new))
        differences = np.abs(new_coef - old_coef)
        sum_of_differences = np.sum(differences)
        #print(f" {i}) Finished computing for n = {n_new} and n = {n_old}. Result: {sum_of_differences}")
        results.append((n_new, n_old, sum_of_differences))
        progress_percentage = (i / total_iterations) * 100
        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        print(f"{time}: {progress_percentage:.2f}% completed")
        i = i+1

    return results

def write_results_to_file(config_file, start_n, end_n, step, output_file, tolerance):
    config_manager = ConfigManager(config_file)
    Y1 = config_manager.get_Y1()
    Y2 = config_manager.get_Y2()
    with open(output_file, 'w') as file:
        file.write("This vector is the result of automatic simulation\n")
        file.write("Each result is the sum of the residues\n")
        file.write("Results are written as: (n+1, n):result\n")
        file.write(f"Y1: {Y1}\n")
        file.write(f"Y2: {Y2}\n")
        file.write("------------------------------------------------\n")
        optimal_n = None
        optimal_result = None
        for result in compute_difference_constants(config_file, start_n, end_n, step, output_file, tolerance):
            n_new, n_old, sum_of_differences = result
            file.write(f"({n_new},{n_old}): {sum_of_differences}\n")
            if sum_of_differences < tolerance and (optimal_result is None or sum_of_differences < optimal_result):
                optimal_n = n_new
                optimal_result = sum_of_differences
        if optimal_n is not None:
            file.write("-------------------------------------------------\n")
            file.write(f"Optimal n: {optimal_n}\n")
            file.write(f"Result for optimal n: {optimal_result}\n")
            file.write(f"Tolerance: {tolerance}\n")
            file.write("-------------------------------------------------\n")
            print("-------------------------------------------------")
            print(f"Optimal n: {optimal_n}")
            print(f"Result for optimal n: {optimal_result}")
            print(f"Tolerance: {tolerance}")
            print("-------------------------------------------------")
        else:
            file.write("-------------------------------------------------\n")
            file.write(f"Optimal n not found within the given tolerance\n")
            file.write(f"Tolerance: {tolerance}\n")
            file.write("-------------------------------------------------\n")
            print("-------------------------------------------------")
            print(f"Optimal n not found within the given tolerance")
            print(f"Tolerance: {tolerance}")
            print("-------------------------------------------------")


if __name__ == "__main__":
    config_file = sys.argv[1]
    start_n = int(sys.argv[2])
    end_n = int(sys.argv[3])
    step = int(sys.argv[4])
    output_file_name = sys.argv[5]
    tolerance = float(sys.argv[6])
    #simulate_autopilot(config_file,start_n,end_n,step)
    write_results_to_file(config_file, start_n, end_n, step, output_file_name, tolerance)

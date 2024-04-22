import sys
from time import gmtime, strftime
import numpy as np
import yaml
import os
from EffectiveElasticTensor import EffectiveElasticTensor
from GenerateMesh import GenerateMesh
from ConfigManager import ConfigManager


def modify_n_in_config(config_file, new_n):
    # load the original YAML configuration file
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    # modify the value of n
    config["simulation_parameters"]["n"] = new_n

    # write the modified data (the new value of n) back to a new temporary YAML file
    temp_config_file = config_file.replace(".yaml", "_temp.yaml")
    with open(temp_config_file, 'w') as file:
        yaml.dump(config, file)

    return temp_config_file


# this method is an extra method that writes partial results into a file
# in other words the result of the tensor for each n is written into a file
def get_partial_results_in_file(config_file, start_n, end_n, step):
    for n in range(start_n, end_n + 1, step):
        # create a modified copy of the original config file for this simulation run
        temp_config_file = modify_n_in_config(config_file, n)

        # generate a mesh and compute the effective elastic tensor using the modified config yaml file
        file_msh = GenerateMesh(temp_config_file).generate_mesh_based_on_sample()

        # write constants into a file
        EffectiveElasticTensor(file_msh, temp_config_file).write_constants_to_file(start_n,end_n,step)

        # remove the temporary config file after use
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


# this method computes the vector of relative residues
# relative residue: the tensor for n+1 and n have different values - n+1 is more accurate
# so the relative residue is the difference between the tensors n+1 and n divided by the
# norm of the tensor n+1. After that the residues for all the effective elastic
# constants within the tensors are summed up. Then the partial result is
# added to an empty list relative_residues. This process is done for all values of n
# within the given range of start_n and end_n with the given step.
# The method returns a list that has all the relative residues
def compute_relative_residues(config_file, start_n, end_n, step, output_file, tolerance):
    config_manager = ConfigManager(config_file)
    Y1 = config_manager.get_Y1()
    Y2 = config_manager.get_Y2()
    sample = ConfigManager(config_file).get_sample()

    # // division without remainder - the result gets rounded to the lowest whole number
    total_iterations = (end_n - start_n) // step
    relative_residues = []
    i = 1
    for n_new in range(start_n + 1, end_n + 1, step):
        # this text is printed out at the begging - for the first cycle
        if n_new == start_n+1:
            print("=================================================")
            print("          AUTOMATIC SIMULATION STARTED")
            print("=================================================")
            print("Settings of the simulation:")
            print(f" - Type of geometry: {sample}")
            print(f" - Y1: {Y1}")
            print(f" - Y2: {Y2}")
            print(f" - n: {start_n} to {end_n}")
            print(f" - step: {step}")
            print(f" - tolerance: {tolerance}")
            print(f" - output: {output_file}")
            print("-------------------------------------------------")
            print("Simulation started:" + strftime("%Y-%m-%d %H:%M:%S", gmtime()))
            print("Progress status of the simulation:")
            print("-------------------------------------------------")

        n_old = n_new - 1

        old_coefficients = np.array(get_only_unique_constants(config_file, n_old))
        new_coefficients = np.array(get_only_unique_constants(config_file, n_new))

        norm_of_tensor_new = np.linalg.norm(new_coefficients)
        differences = np.abs((new_coefficients - old_coefficients) / norm_of_tensor_new)
        sum_of_differences = np.sum(differences)
        relative_residues.append((n_new, n_old, sum_of_differences))

        progress_percentage = (i / total_iterations) * 100
        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        print(f"{time}: ({i}/{total_iterations}) - {progress_percentage:.2f}% completed")
        i = i + 1

    return relative_residues


def write_results_to_file(config_file, start_n, end_n, step, output_file, tolerance):
    config_manager = ConfigManager(config_file)
    Y1 = config_manager.get_Y1()
    Y2 = config_manager.get_Y2()
    sample = config_manager.get_sample()

    with open(output_file, 'w') as file:
        file.write("This vector is the result of automatic simulation\n")
        file.write("Each result is the sum of the residues\n")
        file.write("Results are written as: (n+1, n):result\n")
        file.write(f"Type of geometry: {sample}\n")
        file.write(f"Y1: {Y1}\n")
        file.write(f"Y2: {Y2}\n")
        file.write("------------------------------------------------\n")

        optimal_n = None
        optimal_result = None
        tolerance_met = False

        # this for cycle goes through each result in the list of relative residues
        # it also checks if the tolerance was met
        # if the tolerance was met - the n for which it was met is saved as optimal
        for result in compute_relative_residues(config_file, start_n, end_n, step, output_file, tolerance):
            n_new, n_old, relative_residue = result
            file.write(f"({n_new},{n_old}): {relative_residue}\n")

            if relative_residue < tolerance and not tolerance_met:
                optimal_n = n_new
                optimal_result = relative_residue
                tolerance_met = True

        # checks if optimal n was found - it writes and prints out the information
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

        # if no n within the given range satisfied the tolerance
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
    # arguments that need to be written in command line to run the script
    # example: python3 auto_simulation.py config_file.yaml 56 64 2 results4.txt 0.001
    config_file = sys.argv[1]
    start_n = int(sys.argv[2])
    end_n = int(sys.argv[3])
    step = int(sys.argv[4])
    output_file_name = sys.argv[5]
    tolerance = float(sys.argv[6])

    #simulate_autopilot(config_file,start_n,end_n,step)
    write_results_to_file(config_file, start_n, end_n, step, output_file_name, tolerance)
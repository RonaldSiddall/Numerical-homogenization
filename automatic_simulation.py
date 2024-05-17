import sys
import numpy as np
import yaml
import os
from EffectiveElasticTensor import EffectiveElasticTensor
from GenerateMesh import GenerateMesh
from ConfigManager import ConfigManager
from datetime import datetime, timedelta


def modify_n_in_config(config_file, new_n):
    # loads the original .yaml configuration file
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    # modifies the value of n in the confing file
    config["simulation_parameters"]["n"] = new_n

    # writes the modified data (the new value of n) back to a new temporary .yaml file
    # this .yaml gets deleted after the computation
    temp_config_file = config_file.replace(".yaml", "_temp.yaml")
    with open(temp_config_file, 'w') as file:
        yaml.dump(config, file)

    return temp_config_file


# this method returns all the effective elastic constants + divides the third column by 2
def get_tensor_constants(config_file, n_new):
    temp_config_file = modify_n_in_config(config_file, n_new)
    file_msh = GenerateMesh(temp_config_file).generate_mesh_based_on_sample()
    all_tensor_constants = EffectiveElasticTensor(file_msh, temp_config_file).compute_effect_elast_constants_voigt()
    os.remove(temp_config_file)
    # the last three constants need to be divided by 2 - reason is written in the theory
    all_tensor_constants = np.array([
        [all_tensor_constants[0][0], all_tensor_constants[0][1], all_tensor_constants[0][2]],
        [all_tensor_constants[1][0], all_tensor_constants[1][1], all_tensor_constants[1][2]],
        [all_tensor_constants[2][0]/2, all_tensor_constants[2][1]/2, all_tensor_constants[2][2]/2]])
    return all_tensor_constants


def write_constants_to_file(config_file, n_new, output_file_path_tensor, sample, Y1, Y2):
    tensor_constants = get_tensor_constants(config_file, n_new)
    with open(output_file_path_tensor, 'a') as file:
        file.write("-------------------------------------------------------------------------------\n")
        file.write(f"{sample}, n = {n_new}, Y1 = {Y1}, Y2 = {Y2}\n")
        for constants in tensor_constants:
            for constant in constants:
                file.write(f"{constant}\n")
        file.write("-------------------------------------------------------------------------------\n")


# this method computes the relative residues
# relative residue: the tensor for n+2 and n have different values - n+2 is more accurate
# so the relative residue is the abs. value difference between the tensors n+2 and n divided by the
# norm of the tensor n+2. After that the residues for all the effective elastic
# constants within the tensors are summed up. Then the partial result is
# added to an empty list relative_residues and yielded so that it can be written into the output file
# This process is done for all values of n within the given range of start_n and end_n with the given step.
# The method yields a value of the given relative residue

def compute_relative_residues(config_file, start_n, end_n, step, output_file_tensor, output_file_residues, tolerance):
    config_manager = ConfigManager(config_file)
    Y1 = config_manager.get_Y1()
    Y2 = config_manager.get_Y2()
    sample = config_manager.get_sample()

    total_iterations = (end_n - start_n) // step
    i = 1
    for n_new in range(start_n + 1, end_n + 1, step):
        # Gets the current UTC time
        utc_time = datetime.utcnow()
        # Converts UTC time to CET (which is + 2 hours)
        cet_time = utc_time + timedelta(hours=2)
        # Formats the time string
        cet_time_str = cet_time.strftime("%Y-%m-%d %H:%M:%S")

        if n_new == start_n + 1:
            print("=================================================")
            print("          AUTOMATIC SIMULATION STARTED")
            print("=================================================")
            print("Settings of the simulation:")
            print(f" - type of geometry: {sample}")
            print(f" - Y1: {Y1}")
            print(f" - Y2: {Y2}")
            print(f" - n: {start_n} to {end_n}")
            print(f" - step: {step}")
            print(f" - tolerance: {tolerance}")
            print(f" - output with tensors: {output_file_tensor}")
            print(f" - output with residues: {output_file_residues}")
            print("-------------------------------------------------")
            print("Simulation started:", cet_time_str)
            print("Progress status of the simulation:")
            print("-------------------------------------------------")
            write_constants_to_file(config_file, start_n, output_file_tensor, sample, Y1, Y2)

        # n = m - 2
        n_old = n_new - 2
        old_coefficients = np.array(get_tensor_constants(config_file, n_old + 1))
        new_coefficients = np.array(get_tensor_constants(config_file, n_new + 1))
        write_constants_to_file(config_file, n_new + 1, output_file_tensor, sample, Y1, Y2)

        # Frobenius norm of tensor
        norm_of_tensor_new = np.linalg.norm(new_coefficients)
        differences = np.abs((new_coefficients - old_coefficients) / norm_of_tensor_new)
        relative_residue = np.sum(differences)

        progress_percentage = (i / total_iterations) * 100
        # Prints the time in CET (+2 hours)
        print(f"{cet_time_str}: ({i}/{total_iterations}) - {progress_percentage:.2f}% completed")
        i += 1

        yield n_new + 1, n_old + 1, relative_residue
        if relative_residue < tolerance:
            break


def write_residues_to_file(config_file, start_n, end_n, step, output_file_tensor, output_file_residues, tolerance):
    config_manager = ConfigManager(config_file)
    Y1 = config_manager.get_Y1()
    Y2 = config_manager.get_Y2()
    sample = config_manager.get_sample()

    # Initialize the residues file with the header
    with open(output_file_residues, 'w') as file:
        file.write("This vector is the result of automatic simulation\n")
        file.write("Each result is the sum of the residues\n")
        file.write("Results are written as: (n+2, n):result\n")
        file.write(f"Type of geometry: {sample}\n")
        file.write(f"Y1: {Y1}\n")
        file.write(f"Y2: {Y2}\n")
        file.write("------------------------------------------------\n")

    # Initialize values of optimal_n and tolerance boolean
    optimal_n = None
    optimal_result = None
    tolerance_met = False

    # Process each residue as it is computed and written to the file
    for n_new, n_old, relative_residue in compute_relative_residues(config_file, start_n, end_n, step,
                                                                    output_file_tensor, output_file_residues,
                                                                    tolerance):
        with open(output_file_residues, 'a') as file:
            file.write(f"({n_new},{n_old}): {relative_residue}\n")

        if relative_residue < tolerance and not tolerance_met:
            optimal_n = n_new
            optimal_result = relative_residue
            tolerance_met = True
            break  # Break the loop as tolerance is met

    # Appends the optimal result information if found
    with open(output_file_residues, 'a') as file:
        if optimal_n is not None:
            file.write("-------------------------------------------------\n")
            file.write(f"Optimal n: {optimal_n-2}\n")
            file.write(f"Result for optimal n: {optimal_result}\n")
            file.write(f"Tolerance: {tolerance}\n")
            file.write("-------------------------------------------------\n")
            print("-------------------------------------------------")
            print(f"Optimal n: {optimal_n-2}")
            print(f"Result for optimal n: {optimal_result}")
            print(f"Tolerance: {tolerance}")
            print("-------------------------------------------------")
        else:
            file.write("-------------------------------------------------\n")
            file.write(f"Optimal n not found within the given tolerance\n")
            file.write(f"Tolerance: {tolerance}\n")
            file.write("-------------------------------------------------\n")
            print("-------------------------------------------------")
            print("Optimal n not found within the given tolerance")
            print(f"Tolerance: {tolerance}")
            print("-------------------------------------------------")


if __name__ == "__main__":
    try:
        # Checks if the correct number of command-line arguments are provided
        # if not, gives a warning message
        if len(sys.argv) != 8:
            print("-------------------------------------------------------------------------")
            print("\nAn error occurred during execution.")
            print("Please make sure to enter the command like this:\n")
            print("python <script_name.py> <config_file.yaml> <start_n> <end_n> <step> <output_file_tensor> <output_file_residues> <tolerance>\n")
            print("-------------------------------------------------------------------------")
            sys.exit(1)

        # Extracts command-line arguments
        config_file = sys.argv[1]
        start_n = int(sys.argv[2])
        end_n = int(sys.argv[3])
        step = int(sys.argv[4])
        output_file_tensor = sys.argv[5]
        output_file_residues = sys.argv[6]
        tolerance = float(sys.argv[7])

        # starts the simulation
        write_residues_to_file(config_file, start_n, end_n, step, output_file_tensor, output_file_residues, tolerance)

    except Exception as error_message:
        # Prints error message if an exception occurs
        print("----------------------------------------------------------------------------")
        print("\nAn error occurred during execution. The error message is written below:\n")
        print(str(error_message)+"\n")
        print("\n--------------------------------------------------------------------------")
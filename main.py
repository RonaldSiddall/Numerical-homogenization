import sys
import time
from EffectiveElasticTensor import EffectiveElasticTensor
from ConfigManager import ConfigManager
from GenerateMesh import GenerateMesh


def main(config_file):
    try:
        file_msh = GenerateMesh(config_file).generate_mesh_based_on_sample()
        time_decider = ConfigManager(config_file).get_measure_time_of_computation()
        if time_decider == "yes":
            print("\n=========================================================================\n")
            print("         The effective elastic tensor was successfully computed!")
            print("\n=========================================================================\n")
            print("Additional information about the simulation process:")
            print("------------------------------------------------------")
            print("  - The results were saved in a file named '"
                + ConfigManager(config_file).get_name_of_file_with_tensor()
                + ".txt' that was created in this directory:")
            print("    " + ConfigManager(config_file).get_output_dir_of_file_with_tensor())

            start_time = time.time()
            EffectiveElasticTensor(file_msh, config_file).get_tensor_in_txt_formatted()
            end_time = time.time()
            print("\n  - Time it took to do the computation:", end_time - start_time, "seconds")
        else:
            print("\n=========================================================================\n")
            print("         The effective elastic tensor was successfully computed!")
            print("\n=========================================================================\n")
            print("Additional information about the simulation process:")
            print("------------------------------------------------------")
            print("  - The results were saved in a file named '"
                + ConfigManager(config_file).get_name_of_file_with_tensor()
                + ".txt' that was created in this directory:")
            print("    " + ConfigManager(config_file).get_output_dir_of_file_with_tensor())
            EffectiveElasticTensor(file_msh, config_file).get_tensor_in_txt_formatted()
    except Exception as error_mess:
        # If any error occurs during execution, print the error message
        print("---------------------------------------------------------------------------")
        print("\nAn error occurred during execution. The error message is written below:\n")
        print(str(error_mess) + "\n")
        print("\n-------------------------------------------------------------------------")


if __name__ == "__main__":
    try:
        # Checks if the number of command-line arguments is less than 2
        if len(sys.argv) < 2:
            # If fewer than 2 arguments are provided, prints out a message
            print("-------------------------------------------------------------------------")
            print("\nAn error occurred during execution.")
            print("Please make sure to enter the command like this:\n")
            print("python <absolute_path_to_main.py> <absolute_path_to_config_file.yaml>\n")
            print("-------------------------------------------------------------------------")
            # Exit the script with an error status code
            sys.exit(1)

        # Extract the path to the config file from the command-line arguments
        config_file = sys.argv[1]

        # Calls the main function with the config file path as an argument
        main(config_file)

    except Exception as error_message:
        # If any error occurs during execution, print the error message
        print("----------------------------------------------------------------------------")
        print("\nAn error occurred during execution. The error message is written below:\n")
        print(str(error_message)+"\n")
        print("\n--------------------------------------------------------------------------")
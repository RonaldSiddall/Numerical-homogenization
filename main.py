import sys
import time
from EffectiveElasticTensor import EffectiveElasticTensor
from ConfigManager import ConfigManager
from GenerateMesh import GenerateMesh


# main is used to perform only one computation of mechanical properties based on config_file.yaml
def main(config_file):
    try:
        file_msh = GenerateMesh(config_file).generate_mesh_based_on_sample()
        time_decider = ConfigManager(config_file).get_measure_time_of_computation()
        if time_decider == "yes":
            start_time = time.time()
            EffectiveElasticTensor(file_msh, config_file).get_tensor_in_txt_formatted()
            print("\n=========================================================================\n")
            print("         The effective elastic tensor was successfully computed!")
            print("\n=========================================================================\n")
            print("Settings of the simulation:")
            print(f" - type of geometry: {ConfigManager(config_file).get_sample()}")
            print(f" - Y1: {ConfigManager(config_file).get_Y1()}")
            print(f" - Y2: {ConfigManager(config_file).get_Y2()}")
            print(f" - n: {ConfigManager(config_file).get_n()}")
            print("---------------------------------------------------------------------------")
            print("The results were saved in '"
                  + ConfigManager(config_file).get_name_of_file_with_tensor()
                  + ".txt' that is in this directory:")
            print("    " + ConfigManager(config_file).get_output_dir_of_file_with_tensor())
            end_time = time.time()
            print("---------------------------------------------------------------------------")
            print("\nTime it took to do the computation:", end_time - start_time, "seconds")
        else:
            EffectiveElasticTensor(file_msh, config_file).get_tensor_in_txt_formatted()
            print("\n=========================================================================\n")
            print("         The effective elastic tensor was successfully computed!")
            print("\n=========================================================================\n")
            print("Settings of the simulation:")
            print(f" - type of geometry: {ConfigManager(config_file).get_sample()}")
            print(f" - Y1: {ConfigManager(config_file).get_Y1()}")
            print(f" - Y2: {ConfigManager(config_file).get_Y2()}")
            print(f" - n: {ConfigManager(config_file).get_n()}")
            print("---------------------------------------------------------------------------")
            print("The results were saved in '"
                  + ConfigManager(config_file).get_name_of_file_with_tensor()
                  + ".txt' that is in this directory:")
            print("    " + ConfigManager(config_file).get_output_dir_of_file_with_tensor())
    except Exception as error_mess:
        # If any error occurs during execution, print the error message
        print("---------------------------------------------------------------------------")
        print("\nAn error occurred during execution. The error message is written below:\n")
        print(str(error_mess) + "\n")
        print("---------------------------------------------------------------------------")


if __name__ == "__main__":
    try:
        # Checks if the number of command-line arguments is less than 2
        if len(sys.argv) < 2:
            # If fewer than 2 arguments are provided, prints out a message
            print("-------------------------------------------------------------------------")
            print("\nAn error occurred during execution.")
            print("Please make sure to enter the command like this:\n")
            print("python <main.py> <config_file.yaml>\n")
            print("-------------------------------------------------------------------------")
            # Exit the script with an error status code
            sys.exit(1)

        # Extract the path to the config file from the command-line arguments
        config_file = sys.argv[1]

        # Calls the main function with the config file path as an argument
        main(config_file)

    except Exception as error_message:
        # If any error occurs during execution, prints the error message
        print("----------------------------------------------------------------------------")
        print("\nAn error occurred during execution. The error message is written below:\n")
        print(str(error_message)+"\n")
        print("\n--------------------------------------------------------------------------")
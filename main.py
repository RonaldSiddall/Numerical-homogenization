import time
from EffectiveElasticTensor import EffectiveElasticTensor
from ConfigManager import ConfigManager

config_file = "C:/Plocha/Semestral_project/Python_skripts/config_file.yaml"
file_msh = ("C:/Plocha/Semestral_project/Python_skripts/data_vtu/temp_mesh_for_template.msh")
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
    EffectiveElasticTensor(file_msh, config_file).get_tensor_in_txt()
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
    EffectiveElasticTensor(file_msh, config_file).get_tensor_in_txt()

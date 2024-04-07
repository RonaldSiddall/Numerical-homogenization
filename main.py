from EffectiveElasticTensor import EffectiveElasticTensor

#data source directories
data_source_dir_1 = "C:/Plocha/Semestral project/Python skripts/data_vtu/Case_01/mechanics-000001.vtu"
data_source_dir_2 = "C:/Plocha/Semestral project/Python skripts/data_vtu/Case_02/mechanics-000001.vtu"
data_source_dir_3 = "C:/Plocha/Semestral project/Python skripts/data_vtu/Case_03/mechanics-000001.vtu"
source_dirs = [data_source_dir_1, data_source_dir_2, data_source_dir_3]

name_of_file_with_results = "example"
output_dir = "C:/Plocha/Semestral project/Python skripts/results_elastic_tensor/"

# visualization of individual .vtu files, "stress", "displacement", "region_id". "displacement_divergence" etc.
effective_elastic_tensor = EffectiveElasticTensor(source_dirs)

# Call the visualize_all_vtu_files method on the instance
effective_elastic_tensor.visualize_all_vtu_files("region_id")

# creates a file with the resulting effective elastic tensor
effective_elastic_tensor.get_tensor_in_txt(name_of_file_with_results,output_dir)

#Confirms that the file was created and the output directory is also displayed
print(f"Byl vytvořen soubor {name_of_file_with_results}.txt, který byl uložen v adresáři {output_dir}")

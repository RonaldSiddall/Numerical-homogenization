from file_util import effective_elastic_tensor_to_txt
from visual_util import visualize_all_vtu_files

#data source directories
data_source_dir_1 = ("C:/Plocha/Semestrální projekt/Python skripty/data_vtu/Case_01/mechanics-000001.vtu")
data_source_dir_2 = ("C:/Plocha/Semestrální projekt/Python skripty/data_vtu/Case_02/mechanics-000001.vtu")
data_source_dir_3 = ("C:/Plocha/Semestrální projekt/Python skripty/data_vtu/Case_03/mechanics-000001.vtu")
source_dirs = [data_source_dir_1, data_source_dir_2, data_source_dir_3]

name_of_file_with_results = "example"
output_dir = "C:/Plocha/Semestrální projekt/Python skripty/results_elastic_tensor/"

# visualization of individual .vtu files, stress = "stress", displacement = "displacement" etc.
visualize_all_vtu_files(source_dirs, "displacement")

# creates a file with the resulting effective elastic tensor
effective_elastic_tensor_to_txt(source_dirs, name_of_file_with_results, output_dir)

#Confirms that the file was created and the output directory is also displayed
print(f"Byl vytvořen soubor {name_of_file_with_results}.txt, který byl uložen v adresáři {output_dir}")

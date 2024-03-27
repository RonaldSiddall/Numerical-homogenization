from file_util import elastic_coefficients_to_txt
from computing import visualize_all_vtu_files

data_source_dir_1 = (
    "C:/Plocha/Semestrální projekt/Python skripty/data_vtu/Case_01/mechanics-000001.vtu"
)
data_source_dir_2 = (
    "C:/Plocha/Semestrální projekt/Python skripty/data_vtu/Case_02/mechanics-000001.vtu"
)
data_source_dir_3 = (
    "C:/Plocha/Semestrální projekt/Python skripty/data_vtu/Case_03/mechanics-000001.vtu"
)
source_dirs = [data_source_dir_1, data_source_dir_2, data_source_dir_3]

name_of_file_with_results = "ukazka"
output_dir = "C:/Plocha/"

# visualization of individual .vtu files, stress = "stress", displacement = "displacement" etc.
visualize_all_vtu_files(source_dirs, "displacement")

# creates a file with the resulting effective elastic tensor
elastic_coefficients_to_txt(source_dirs, name_of_file_with_results, output_dir)

print(
    f"Byl vytvořen soubor {name_of_file_with_results}.txt, který byl uložen v adresáři {output_dir}"
)

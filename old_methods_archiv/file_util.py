import os
import shutil
from EffectiveElasticTensor import EffectiveElasticTensor
from computing import compute_final_constants_voigt_form_whole_tensor

"""""
Tyto metody jsem připravil pro případné přemísťovaní souborů, teď nejsou užívané, protože
mám testovací zdrojové soubory zkopírované v adresáři data_vtu

def extract_specific_file(source_file_path, destination_dir):
    filename = os.path.basename(source_file_path)
    destination_file_path = os.path.join(destination_dir, filename)
    shutil.copyfile(source_file_path, destination_file_path)


def relocate_3_files(source_dirs, destination_dirs):
    for source_dir in source_dirs:
        for destination_dir in destination_dirs:
            extract_specific_file(source_dir, destination_dir)
"""


def effective_elastic_tensor_to_txt(vtu_file_dirs, name_of_file, file_path):
    coefficients = compute_final_constants_voigt_form_whole_tensor(vtu_file_dirs)
    file_path = file_path + name_of_file + ".txt"
    with open(file_path, "w") as txt_file:
        txt_file.write(
            "============================================================================================\n"
        )
        txt_file.write(
            "                    Effective elastic tensor in matrix form for 2D problems\n"
        )
        txt_file.write(
            "============================================================================================\n\n"
        )
        txt_file.write(
            f"            {coefficients[0][0]}           {coefficients[1][0]}      {coefficients[2][0]/2}\n"
        )
        txt_file.write(
            f"C =         {coefficients[0][1]}         {coefficients[1][1]}       {coefficients[2][1]/2}\n"
        )
        txt_file.write(
            f"            {coefficients[0][2]}          {coefficients[1][2]}     {coefficients[2][2]/2}\n\n\n"
        )
        txt_file.write(
            "--------------------------------------------------------------------------------------------\n"
        )
        txt_file.write("This result was computed with these files:\n")
        for vtu_file in vtu_file_dirs:
            txt_file.write(f"{vtu_file}\n")

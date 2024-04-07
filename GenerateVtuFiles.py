import numpy as np
import sympy as sp
from ruamel.yaml import YAML
yaml = YAML()


class GenerateVtuFiles:
    def __init__(self, file_msh, Y1, Y2, E1, E2, E3):
        self.mesh = file_msh
        self.Y1 = Y1
        self.Y2 = Y2
        self.E1 = E1
        self.E2 = E2
        self.E3 = E3

    def get_boundary_conditions_strings(self):
        x, y = sp.symbols('x, y')
        vector_xy = np.array([x, y])

        # np.dot is the dot product of matrix E1 and the vector_xy = [x, y]
        u1 = np.dot(self.E1, vector_xy)
        u2 = np.dot(self.E2, vector_xy)
        u3 = np.dot(self.E3, vector_xy)

        # the lines of code below transform the vectors (1D arrays) to strings in the needed format
        # example case for E1 = [[1, 0], [0, 0]]
        # => u1 = E1 dot [x, y] => u1 = [x 0] (an 1D array - vector)
        # this vector is changed to a string without the brackets (done by str(u1)[1:-1])
        # so we get the string "x 0", after that we replace the " " by ", ".
        # lastly we add a zero and the brackets so the final string format is [x, 0, 0]
        # in summary: vector [x 0] -> string [x, 0, 0]
        u1_s = "[" + str(u1)[1:-1].replace(" ", ",") + ",0" + "]"
        u2_s = "[" + str(u2)[1:-1].replace(" ", ",") + ",0" + "]"
        u3_s = "[" + str(u3)[1:-1].replace(" ", ",") + ",0" + "]"
        return u1_s, u2_s, u3_s

    def get_yamls(self):
        names_files = ["results1.yaml", "results2.yaml", "results3.yaml"]
        vector_u = self.get_boundary_conditions_strings()
        file_msh = "/Plocha/Semestral project/Python skripts/data_vtu/testing_template.msh"
        Y1 = self.Y1
        Y2 = self.Y2
        for i in range(3):
            with open("C:/Plocha/Semestral project/Python skripts/data_vtu/template.yaml", 'r') as file:
                data = yaml.load(file)
                data['problem']['mesh']['mesh_file'] = "/C"+ file_msh
                data['problem']['flow_equation']['mechanics_equation']['input_fields'][0]['young_modulus'] = Y1
                data['problem']['flow_equation']['mechanics_equation']['input_fields'][1]['young_modulus'] = Y2
                data['problem']['flow_equation']['mechanics_equation']['input_fields'][2]['bc_displacement']['value'] = vector_u[i]
            with open("C:/Plocha/Semestral project/Python skripts/data_vtu/outputs/"+names_files[i], 'w') as file:
                yaml.dump(data, file)
            with open("C:/Plocha/Semestral project/Python skripts/data_vtu/outputs/"+names_files[i], "r") as file:
                content = file.read()
                content = content.replace("'"+vector_u[i]+"'", vector_u[i])
            with open("C:/Plocha/Semestral project/Python skripts/data_vtu/outputs/"+names_files[i], "w") as file:
                file.write(content)
    """""
    def extract_specific_file(source_file_path, destination_dir):
        filename = os.path.basename(source_file_path)
        destination_file_path = os.path.join(destination_dir, filename)
        shutil.copyfile(source_file_path, destination_file_path)

    def relocate_3_files(source_dirs, destination_dirs):
        for source_dir in source_dirs:
            for destination_dir in destination_dirs:
                extract_specific_file(source_dir, destination_dir)

    """
from GenerateVtuFiles import GenerateVtuFiles

file_msh = "C:/Plocha/Semestral project/Python skripts/data_vtu/testing_template.msh"
Y1 = 100
Y2 = 50
E1 = [[2, 0], [0, 0]]
E2 = [[0, 0], [0, 2]]
E3 = [[0, 2], [2, 0]]

temp = GenerateVtuFiles(file_msh, Y1, Y2, E1, E2, E3)
temp.get_yamls()




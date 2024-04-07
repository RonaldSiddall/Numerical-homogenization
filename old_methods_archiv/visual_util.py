import pyvista as pv


def visualize_vtu_file_(vtu_file, what_display):
    mesh = pv.UnstructuredGrid(vtu_file)
    mesh.cell_data.get(what_display)
    mesh.plot(scalars=what_display)


def visualize_all_vtu_files(vtu_dirs, what_display):
    for vtu_file in vtu_dirs:
        visualize_vtu_file_(vtu_file, what_display)

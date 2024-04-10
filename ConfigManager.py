import yaml


class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file

    def load_config(self):
        with open(self.config_file, "r") as file:
            config_data = yaml.safe_load(file)
        return config_data

    def get_config_file(self):
        return self.config_file

    def get_n(self):
        return self.load_config()["simulation_parameters"]["n"]

    def get_sample(self):
        return self.load_config()["simulation_parameters"]["sample"]

    def get_Y1(self):
        return self.load_config()["simulation_parameters"]["Y1"]

    def get_Y2(self):
        return self.load_config()["simulation_parameters"]["Y2"]

    def get_E1(self):
        return self.load_config()["simulation_parameters"]["E1"]

    def get_E2(self):
        return self.load_config()["simulation_parameters"]["E2"]

    def get_E3(self):
        return self.load_config()["simulation_parameters"]["E3"]

    def get_dir_where_yamls_are_created(self):
        return self.load_config()["directories"]["dir_where_yamls_are_created"]

    def get_absolute_path_to_yaml_template(self):
        return self.load_config()["directories"]["absolute_path_to_yaml_template"]

    def get_directory_where_vtus_are_created(self):
        return self.load_config()["directories"]["directory_where_vtus_are_created"]

    def get_name_of_file_with_tensor(self):
        return self.load_config()["results_file_settings"]["name_of_file_with_tensor"]

    def get_output_dir_of_file_with_tensor(self):
        return self.load_config()["results_file_settings"]["output_dir_of_file_with_tensor"]

    def get_delete_yaml_dir_after_simulation(self):
        return self.load_config()["additional_settings"]["delete_yaml_dir_after_simulation"]

    def get_delete_vtu_dir_after_simulation(self):
        return self.load_config()["additional_settings"]["delete_vtu_dir_after_simulation"]

    def get_want_to_display_visualisation(self):
        return self.load_config()["additional_settings"]["want_to_display_visualisation"]

    def get_what_to_display(self):
        return self.load_config()["additional_settings"]["what_to_display"]

    def get_change_names_of_computed_yamls(self):
        return self.load_config()["additional_settings"]["change_names_of_computed_yamls"]

    def get_new_names_of_yamls(self):
        return self.load_config()["additional_settings"]["new_names_of_yamls"]

    def get_change_names_of_computed_output_dirs(self):
        return self.load_config()["additional_settings"]["change_names_of_computed_output_dirs"]

    def get_new_names_of_output_dirs(self):
        return self.load_config()["additional_settings"]["new_names_of_output_dirs"]

    def get_change_names_of_computed_vtu_files(self):
        return self.load_config()["additional_settings"]["change_names_of_computed_vtu_files"]

    def get_new_names_of_vtu_files(self):
        return self.load_config()["additional_settings"]["new_names_of_vtu_files"]

    def get_measure_time_of_computation(self):
        return self.load_config()["additional_settings"]["measure_time_of_computation"]

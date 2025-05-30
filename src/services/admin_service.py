import os
from pprint import pprint
from src.services.service import Service
from src.admin.admin import init_admin


class AdminService(Service):
    def __init__(self, name, output_dir, interfaces, admin):
        super().__init__(name=name, output_dir=output_dir, interfaces=interfaces)
        self.admin_list = admin
        return

    def run(self):
        self.logger.info("Admin service start")

        # Data analysis
        for admin_conf in self.admin_list:

            admin_conf['output_dir'] = os.path.join(self.output_dir, admin_conf['name'])
            admin = init_admin(config=admin_conf, output_interface=self.output_interface)

            output_tmp = admin.run()

            self.output.append(output_tmp)

        self.logger.info("Admin service end")

        return self.output


# if self.input_interface.datasets_details_file is not None:

# TODO Questi vanno spostati in admin
# if len(self.input_interface.datasets) == 0 and self.input_interface.limit_rows != 0:
#     raise Exception(f"ERROR: No datasets provided")
#
# if len(self.input_interface.datasets) == 0 and self.input_interface.limit_rows == 0:
#     # Clean db
#     output.append("Database cleaned")


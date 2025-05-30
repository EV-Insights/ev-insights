import os
from pprint import pprint
from src.services.service import Service
from src.analysis.analysis import init_analysis


class AnalysisService(Service):
    def __init__(self, name, output_dir, interfaces, analysis):
        super().__init__(name=name, output_dir=output_dir, interfaces=interfaces)
        self.analysis_list = analysis
        return

    def run(self):

        self.logger.info("Analysis service start")

        output_dict = {}

        # Data analysis
        for analysis_conf in self.analysis_list:

            if 'id' in analysis_conf.keys():
                analysis_name = f"{analysis_conf['id']}_{analysis_conf['name']}"
            else:
                analysis_name = f"{analysis_conf['name']}"
            analysis_conf['output_dir'] = os.path.join(self.output_dir, analysis_name)
            full_custom_mode = analysis_conf['full_custom_mode'] \
                if "full_custom_mode" in analysis_conf.keys() and analysis_conf['full_custom_mode'] is True else False
            analysis = init_analysis(config=analysis_conf,
                                     input_interface=self.input_interface,  # if full_custom_mode is True else None,
                                     output_interface=self.output_interface)  # if full_custom_mode is True else None)

            if analysis:
                self.logger.info("Analysis: %s" % analysis.name)

                if analysis.full_custom_mode:
                    # Get data, run analysis and save results independently
                    output = analysis.run()

                else:
                    # Data gathering from input interface
                    df = self.input_interface.get_data(data_selection=analysis.data_selection)

                    # Load data into an Analysis object
                    analysis.load_data(df=df)

                    # Check data for input validation
                    analysis.check_data()

                    # Data enrichment
                    analysis.custom_settings()

                    # Run analysis
                    analysis.run()

                    # Save analysis output to file
                    # TODO this should use interface methods, move save_output_to_file into interface
                    if analysis.save_results:
                        analysis.save_output_to_file()

                    # Get analysis results
                    output = analysis.get_results()

                output_dict.update({f"{analysis_name}": output})

        self.logger.info("Analysis service end")

        return output_dict

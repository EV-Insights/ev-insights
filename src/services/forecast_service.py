import os
from pprint import pprint
from src.services.service import Service
from src.forecast.forecast import init_forecast


class ForecastService(Service):
    def __init__(self, name, output_dir, interfaces, models_dir, forecast):
        super().__init__(name=name, output_dir=output_dir, interfaces=interfaces)
        self.models_dir = models_dir
        self.forecasts_list = forecast
        return

    def run(self):
        self.logger.info("Forecast service start")

        output_dict = {}

        # Forecast
        for forecast_conf in self.forecasts_list:

            if 'id' in forecast_conf.keys():
                forecast_name = f"{forecast_conf['id']}_{forecast_conf['name']}"
            else:
                forecast_name = f"{forecast_conf['name']}"
            forecast_conf['output_dir'] = os.path.join(self.output_dir, forecast_name)
            full_custom_mode = forecast_conf['full_custom_mode'] \
                if "full_custom_mode" in forecast_conf.keys() and forecast_conf['full_custom_mode'] is True else False
            forecast = init_forecast(config=forecast_conf,
                                     models_dir=self.models_dir,
                                     input_interface=self.input_interface if full_custom_mode is True else None,
                                     output_interface=self.output_interface if full_custom_mode is True else None)

            if forecast:
                self.logger.info("Forecast: %s" % forecast.name)

                output = None
                if forecast.full_custom_mode:
                    # Get data, train the model, predict the forecast and save results independently
                    output = forecast.run()

                else:
                    # Data gathering from input interface
                    df = self.input_interface.get_data(data_selection=forecast.data_selection)

                    # Data gathering from input interface or mlflow interface
                    model = None
                    prediction = None
                    experiment_id = None
                    run_id = None
                    if forecast.mode == 'predict':
                        if self.mlflow_interface:
                            experiment_id, run_id, model = self.mlflow_interface.get_model(algo=forecast.algo,
                                                                                           model_name=forecast.model_name)
                        else:
                            prediction = self.input_interface.get_prediction(actor=forecast.actor,
                                                                             actor_id=forecast.actor_id,
                                                                             date=forecast.date)

                    # Load data into Forecast object
                    forecast.load_data(df=df, prediction=prediction, model=model)

                    # Check data for input validation
                    forecast.check_data()

                    # Data enrichment
                    forecast.feature_engineering()

                    # Run forecast (this will train the model or predict the forecast, based on selected mode)
                    forecast.run()

                    # Save forecast retults (train or predict, based on selected mode)
                    if forecast.save_results:
                        if forecast.mode == 'train':
                            if self.mlflow_interface:
                                self.mlflow_interface.save_forecast_model(forecaster_name=forecast.name,
                                                                          algo=forecast.algo,
                                                                          results=forecast.results)
                            else:
                                self.output_interface.save_forecast_model(forecaster_name=forecast.name,
                                                                          results=forecast.results,
                                                                          file_path=self.models_dir)
                        elif forecast.mode == 'predict':
                            self.output_interface.save_forecast_prediction(forecaster_name=forecast.name,
                                                                           actor=forecast.actor,
                                                                           model=model,
                                                                           experiment_id=experiment_id,
                                                                           run_id=run_id,
                                                                           results=forecast.results,
                                                                           algo=forecast.algo)

                    # Get forecast results
                    if forecast.mode == 'train':
                        output = forecast.get_train_results(keys=['metrics'])
                    elif forecast.mode == 'predict':
                        output = forecast.get_predict_results()

                output_dict.update({f"{forecast_name}": output})

        self.logger.info(f"Forecast service output: {output_dict}")
        self.logger.info("Forecast service end")

        return output_dict


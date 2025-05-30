# Tutorial for Researchers and Data Scientists use case

## Overview
`Researchers` and `Data Scientists` typically require substantial amounts of data to conduct their research, which a single dataset often 
fails to provide. It is widely recognized that obtaining a single dataset containing a large number of charging session records is uncommon. 
Consequently, these users frequently engage in the process of identifying and merging multiple datasets to achieve a sufficient sample size. 
This phase of their work often demands significant resources due to the heterogeneity of the available data.
EV-Insights aims to address this challenge by facilitating the efficient and resource-effective aggregation of diverse datasets. The steps 
required to add a new dataset include uploading the dataset to the designated input folder, adding its metadata to the `dataset_details.csv` 
file, and creating a small custom function for data import, which can be easily developed by referencing existing implemented functions, 
basically used for mapping the data with the database structure. The remaining infrastructure ensures that the data is read, processed and 
loaded into the database while maintaining consistency with other datasets. This allows researchers and data scientists to focus more on 
developing advanced analytical and forecasting methods that are directly relevant to their research objectives.

The `Analysis` module provides a framework for managing and executing different types of data analyses in a standardized way. It defines a 
base class that ensures consistency across various analyses and includes utility functions to initialize and dynamically load specific data 
and functions based on configuration files formatted in JSON.
Each analysis follows a consistent structure, starting with data retrieval, validation and preparation. Custom settings can be applied to 
run the analysis with specific requirements, such as adding new features or filtering data. The main logic of the analysis is implemented 
in the “run” method, which processes the data and generates outputs like visualizations or summary statistics. Results can be saved in 
various formats, including images, JSON, XLSX, and PDF, depending on the analysis type. Each analysis can be executed on individual 
datasets or across all datasets imported into the database. Thanks to the standardized data format and to a configurable parameter, 
datasets can be merged, enabling more insights from combined data sources. In most analysis, an optional clipping range can be applied to 
make some filters during data retrieval (i.e. by energy demand, plug in datetime, etc.).

The `Forecast` module provides a structured framework for building and using predictive models within the EV-Insights platform. It provides 
functionality to create and use forecasting models for predicting specific outcomes, such as energy consumption or charging duration. 
Similar to the Analysis module, it is implemented to ensure consistency across different forecasting modules, by starting with data 
validation and preparation and the possibility to apply custom settings to run the module with specific requirements, such as adding 
specific features or filtering data. Each implementation must include the two main function: train, for generating new models or updating 
existing ones, and predict, for producing inference results.

This tutorial explains how to configure, initialize, and run the `Analysis` and the `Forecast` services.

---

## Prerequisites
- Python installed on your system.
- Required dependencies installed `pip install -r requirements.txt`
- Proper configuration files (`conf/cli/conf_cli_analysis_db.json`).
- Datasets available in the database for analysis and forecasting. Ingestion service should be run first.

---

## Configuration

### Analysis
The full list of available analysis are available in the configuration file `conf/cli/conf_cli_analysis_db.json`. 
All analysis can be run by enabling the `enabled` field to `true` for the desired analysis.

In case you want to further customize the analysis, below is the description of each field in the stats analysis configuration. 
You can find some examples in the full `conf/cli/conf_cli_analysis_db.json` file.

- **`id`**: Unique identifier for the analysis configuration.
- **`name`**: Name of the analysis (e.g., `stats`).
- **`info`**: Description or additional information about the analysis.
- **`enabled`**: Boolean flag indicating whether the analysis is active (`true`) or not (`false`).
- **`full_custom_mode`**: Boolean flag to enable full customization of the analysis process.
- **`show_images`**: Boolean flag to display images generated during the analysis.
- **`save_images`**: Boolean flag to save images generated during the analysis.
- **`save_results`**: Boolean flag to save the results of the analysis.
- **`data_selection.datasets`**: List of datasets to be included in the analysis.
- **`data_selection.merge_datasets`**: Boolean flag to indicate whether datasets should be merged before analysis.
- **`data_selection.fields`**: Specifies the fields to be analyzed:
  - **`dataset_name`**: Name of the dataset.
  - **`user_id`**: Identifier for the user.
  - **`plug_in_datetime`**: Date and time when the plug-in occurred (`from` and `to` values can be specified).
  - **`plug_out_datetime`**: Date and time when the plug-out occurred (`from` and `to` values can be specified).
  - **`energy_supplied`**: Amount of energy supplied during the session.
- **`custom_params.entity`**: Entity type for the analysis (e.g., `dataset`).
- **`custom_params.id`**: Identifier for the entity being analyzed.
- **`custom_params.plug_duration`**: Duration of the plug-in session (optional).
- **`custom_params.energy_supplied_clip`**: Range for clipping the energy supplied values:
  - **`min`**: Minimum value for energy supplied.
  - **`max`**: Maximum value for energy supplied.

If you want to develop an additional analysis, please follow the `Developers` tutorial on how to create a new analysis module.

### Forecast
Forecast module services can be identified in two different categories: train and predict.

The full list of available forecast are available in the configuration files:
- `conf_cli_forecast_train_db_mlflow.json` which contains the configurations for training the models.
- `conf_cli_forecast_predict_schedule_db_mlflow` which contains the configurations for running predictions.

Configuration files are very similar to the analysis one, with the main difference being that they contain the name
of the model and additional parameters for running the training or prediction.

If you want to develop an additional forecast, please follow the `Developers` tutorial on how to create a new forecast module.

---

## Start the Service

### Analysis

To start the Analysis Service, follow these steps:

1. Ensure your working directory is set to the project root
2. Run the service using the command:
   ```bash
   python src/__main__.py -c conf/cli/conf_cli_analysis_db.json
   ```
3. The service will process the datasets specified in the configuration file following the selected analysis.
4. Monitor the logs in the `log/` directory for any issues or progress updates.
5. Once the service completes its run, the results will be saved in the specified `output_dir` folder.


### Forecast

To start the Forecast Service for training a model, follow these steps:

1. Ensure your working directory is set to the project root
2. Run the service using the command:
   ```bash
   python src/__main__.py -c conf/cli/conf_cli_forecast_train_db_mlflow.json
   ```
3. The service will initialize and start processing the datasets specified in the configuration file.
4. Monitor the logs in the `log/` directory for any issues or progress updates.
5. Once the service completes its run, the results will be saved in the specified `output_dir` folder.


To start the Forecast Service for running predictions, follow these steps:

1. Ensure your working directory is set to the project root
2. Run the service using the command:
   ```bash
   python src/__main__.py -c conf/cli/conf_cli_forecast_predict_query_db.json
   ```
3. The service will initialize and start processing the datasets specified in the configuration file.
4. Monitor the logs in the `log/` directory for any issues or progress updates.
5. Once the service completes its run, the results will be saved in the specified `output_dir` folder.
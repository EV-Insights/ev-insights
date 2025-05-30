# Tutorial for Single User use case

## Overview
`DSO`, `charging station owners`, `private users`, or any interested party can leverage EV-Insights to process its dataset and extract valuable 
insights or predictions about charging behavior. The workflow is straightforward: after ingesting the dataset as described in the previous 
section, the user can run one or more pre-configured analysis by selecting the analysis type. In addition, if more specific information is 
needed, the user can adjust a few parameters, such as time or energy ranges or filter results by dataset, user, or station IDs.
Once configured, EV-Insights dynamically loads the appropriate analysis module from its library, ensuring that the selected analysis aligns 
with the needs. It retrieves the relevant data from the database, validates it, and processes it according to the logic defined in the 
chosen module. The results, whether they are statistical summaries or predictions, are saved in a structured format and can be visualized 
for better interpretation in different file formats like images, spreadsheets or pdf documents.

The analysis `stats` is the main analysis responsible for generating statistical insights from the data stored in the system. 
It supports exporting results in multiple formats, including JSON, XLSX, and PDF.

This tutorial explains how to configure, initialize, and run the analysis `stats` service.

---

## Prerequisites
- Python installed on your system.
- Required dependencies installed `pip install -r requirements.txt`
- Proper configuration files (`conf/cli/conf_cli_analysis_db.json`).
- Datasets available in the database for analysis. Ingestion service should be run first.

---

## Configuration
The analysis `stats` relies on the configuration file `conf/cli/conf_cli_analysis_db.json`. 
For a fast analysis setup, you can use the provided example configuration file by simply modifying the dataset list to include the ones 
you want to analyze.
Moreover, set the `enabled` field to `true` only for the analysis named `stats` where `info` is `Stats dataset`. Set to `false` all other 
analyses.

```json
    "name": "stats",
    "info": "Stats dataset",
    "enabled": true,
```

Below is the full example structure:

```json
{
    "service": "analysis",
    "services": {
        "analysis": {
            "name": "analysis",
            "output_dir": "service/analysis",
            "interfaces": {
                "input": {
                    "name": "PostgreSql",
                    "type": "input",
                    "output_dir": "interface/input",
                    "host": "localhost",
                    "port": 5432,
                    "user": "evinsights",
                    "password": "evinsights",
                    "database": "evinsights"
                },
                "output": {
                    "name": "PostgreSql",
                    "type": "output",
                    "output_dir": "interface/output",
                    "host": "localhost",
                    "port": 5432,
                    "user": "evinsights",
                    "password": "evinsights",
                    "database": "evinsights"
                }
            },
            "utils": {
                "output_dir": "../../data/output/",
                "logger": {
                    "output_dir": "log/",
                    "email_notifications": false,
                    "to_address_list": []
                }
            },
            "analysis": [
                {
                    "id": 11,
                    "name": "stats",
                    "info": "Stats dataset",
                    "enabled": true,
                    "full_custom_mode": true,
                    "show_images": true,
                    "save_images": true,
                    "save_results": true,
                    "data_selection": {
                        "datasets": ["ACN_Caltech"],
                        "merge_datasets": false,
                        "fields": {
                            "dataset_name": null,
                            "user_id": null,
                            "plug_in_datetime": {
                                "from": null,
                                "to": null
                            },
                            "plug_out_datetime": {
                                "from": null,
                                "to": null
                            },
                            "energy_supplied": null
                        }
                    }
                }
            ]
        }
    }
}
```

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

---

## Start the Service

To start the Analysis Service `stats`, follow these steps:

1. Ensure your working directory is set to the project root
2. Run the service using the command:
   ```bash
   python src/__main__.py -c conf/cli/conf_cli_analysis_db.json
   ```
3. The service will process the datasets specified in the configuration file following the selected analysis.
4. Monitor the logs in the `log/` directory for any issues or progress updates.
5. Once the service completes its run, the results will be saved in the specified output directory (`../../data/output/`).
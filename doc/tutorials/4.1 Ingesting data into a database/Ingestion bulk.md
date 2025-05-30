# Ingestion Service Tutorial - Bulk Data Ingestion

## Overview
The Ingestion module is responsible for managing the complete data acquisition process. This encompasses reading, pre-processing, cleaning, 
and inserting data into the PostgreSQL db. It is designed to handle a variety of data sources, enabling the flexibility required to 
accommodate both entire datasets and real-time, point-specific data as it becomes available.
For public datasets, the ingestion process begins with a pre-processing phase. The module is able of reading files in multiple formats, 
including CSV, XLSX, and JSON, ensuring compatibility with various data sources. Each dataset undergoes a specific pre-processing routine 
used to standardise the data according to the proposed data model. This standardisation is essential for maintaining consistency and 
reliability in the database. During this phase, data cleaning is also performed, where entries with null values or anomalies are removed 
to ensure that only high-quality data is retained for analysis. In the case of real-time data, it is assumed that the incoming information 
adheres to a pre-agreed format. This standardization facilitates seamless integration into the system, allowing for immediate processing 
and analysis without the need for extensive pre-processing steps. Overall, the Ingestion module guarantees that data is accurately and 
efficiently prepared for subsequent analysis and forecasting tasks.

The `Ingestion Service` supports two types of data ingestion:
1. **Bulk ingestion**: The Bulk Ingestion process is designed to handle and process one or multiple datasets with different file formats 
and content in one go. This is mainly used to ingest an entire dataset, such as a public dataset. 
2. **Table ingestion**: The Table Ingestion process allows adding new pieces of information to specific tables in the system, such as 
datasets, users, charging stations, and charging sessions. This process is designed to be flexible and efficient so that new data can 
be added without reprocessing everything in the database allowing continuous data ingestion.

This tutorial guides you through the configuration, initialization, and execution of the ingestion service for `bulk` data ingestion.


---

## Prerequisites
- Python installed on your system.
- Required dependencies installed `pip install -r requirements.txt`
- Proper configuration files 
  - API: `conf/cli/conf_cli_ingestdata.json`
  - CLI: `conf/cli/conf_cli_ingestion_bulk.json`

---

## Configuration
The first step is to insert the desired dataset details into the configuration file `data/input/datasets_details.csv`.
This file contains metadata about the datasets to be ingested, such as dataset name, url, description, owner, license, file type, and more.

The file includes:
- **`dataset_name`**: Name of the dataset.
- **`dataset_url`**: URL where the dataset can be accessed.
- **`dataset_description`**: Brief description of the dataset.
- **`dataset_owner`**: Owner or organization responsible for the dataset.
- **`dataset_country`**: Country associated with the dataset.
- **`dataset_region`**: Region (if applicable).
- **`dataset_city`**: City (if applicable).
- **`dataset_active`**: Indicates if the dataset is active (`True` or `False`).
- **`dataset_file_name`**: Name of the file containing the dataset.
- **`dataset_sheet_name`**: Sheet name (if applicable, for Excel files).
- **`dataset_file_type`**: File type (e.g., `csv`, `json`, `xlsx`).
- **`dataset_delimiter`**: Delimiter used in the file (e.g., `,`, `;`).
- **`dataset_encoding`**: Encoding format (e.g., `UTF-8`, `latin1`).
- **`dataset_license`**: License type for the dataset.
- **`dataset_charging_point_type`**: Type of charging point (e.g., `public`, `private`).
- **`dataset_notes`**: Additional notes about the dataset.


Then, the configuration file must be configured to choose which datasets to ingest.
An example of a configuration file for the ingestion service is provided in `conf/cli/conf_cli_ingestion_table.json`, 
where the input interface is defined to handle bulk ingestion of datasets from files.

```json
"interfaces": {
    "input": {
        "name": "File",
        "type": "input",
        "input_dir": "../../data/input/public_datasets/",
        "output_dir": "interface/input",
        "limit_rows": null,
        "input_data_type": "bulk",
        "datasets_list": ["ACN_Caltech", "AMB_Barcellona", "Elaad", "OLEV", "BeLib", "Harvard_dataverse", "Norway_12loc"],
        "datasets_details_file": "data\\input\\datasets_details.csv"
    }
}
```

Below is the description of all fields under the `interfaces` tag in the configuration file:

- **`input`**: Defines the input interface configuration.
  - **`name`**: Name of the input interface (e.g., `File`).
  - **`type`**: Type of the interface (e.g., `input`).
  - **`input_dir`**: Directory containing the input datasets.
  - **`output_dir`**: Directory where anything needed could be stored.
  - **`limit_rows`**: Limits the number of rows processed from the input datasets (`null` for no limit). This is useful for development and testing purposes.
  - **`input_data_type`**: Specifies the ingestion type (`bulk` or `table`).
  - **`datasets_list`**: List of dataset names to be ingested.
  - **`datasets_details_file`**: Path to the CSV file containing metadata about the datasets.

---

## Initialization
For bulk ingestion, ensure `input_data_type` is set to `bulk`. The service will:
1. Insert dataset details.
2. Insert charging station details.
3. Insert user data.
4. Insert charging session data.

For each dataset, create a separate folder within the `input_dir` directory, named consistently with the dataset’s name, and upload the 
corresponding files into it. Ensure that the filenames of the data to be imported match those specified in the datasets_details.csv file.

---

## Start the service

To start the Ingestion Service `bulk`, follow these steps:

1. Ensure your working directory is set to the project root
2. Run the service using the command:
   ```bash
   python src/__main__.py -c conf/cli/conf_cli_ingestion_bulk.json
   ```
3. The service reads the datasets specified in the configuration file from their corresponding files and imports them into the database.
4. Monitor the logs in the `log/` directory for any issues or progress updates.


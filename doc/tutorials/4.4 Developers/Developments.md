# Ingestion Service Tutorial

## Overview
EV-Insights is also designed to engage `developers` who are interested in enhancing and extending its functionality. For instance, developers 
can implement custom functions to preprocess and transform datasets, ensuring seamless compatibility with the EV-Insights infrastructure. 
Additionally, they can create new customized input and output interfaces to support a broader range of file formats and databases and 
implement new  APIs to provide additional services. Furthermore, they can integrate entirely new services, which can be incorporated into 
the existing framework with ease.
To facilitate this, EV-Insights is developed following best practices in software engineering. These include principles such as modular 
design, which ensures that individual components can be developed, tested, and maintained independently; maintainability, achieved through 
clean, well-documented, and readable code; and high customizability, allowing users to adapt EV-Insights to their specific needs with 
minimal effort.
This tutorial will guide you through the creation of a `new service` and a `new analysis service`. The same tutorial can be followed for 
implementing a `new forecasting service`, a `new ingestion service`, or a `new admin service`.

---

## 1. New Service

### 1.1. Define the Service Name
Choose a unique name for your service and add it to the `SERVICES` set in `src/services/service.py`:
```python
SERVICES = {"analysis", "forecast", "ingestion", "admin", "new_service"}
```

### 1.2. Create the Service Class
Create a new file for your service in the `src/services/` directory, e.g., `src/services/new_service.py`. Define the class by extending the 
`Service` base class.

```python
import logging
from src.services.service import Service

class NewService(Service):
    def __init__(self, name, output_dir, interfaces, custom_config):
        super().__init__(name, output_dir, interfaces)
        self.custom_config = custom_config
        self.logger.info("Initialized NewService with custom configuration")

    def run(self):
        self.logger.info("Running NewService...")
        # Add your service logic here
        pass
```

### 1.3. Update the `init_service` Function
Modify the `init_service` function in `src/services/service.py` to include your new service.

```python
elif service_name == 'new_service':
    from src.services.new_service import NewService
    service = NewService(name=config['name'],
                         output_dir=config['output_dir'],
                         interfaces=config['interfaces'],
                         custom_config=config['custom_config'])
```

### 1.4. Create a Configuration File
Add a configuration file for your service in the `conf/cli/` directory, e.g., `conf/cli/conf_cli_new_service.json` using the configuration 
files of the existing services as a reference. 

### 1.5. Implement the Service Logic
Implement the logic for your service in the `run` method of your service class. This method should contain the core functionality of your 
service.

---

# 2. New Analysis

### 2.1. Define the Analysis Name
Add the name of your new analysis to the `ANALYSIS` set in `src/analysis/analysis.py`:
```python
ANALYSIS = {"_sample_analysis", "animated_energy_duration", "new_analysis"}
```

---

### 2. Create the Analysis Class
Create a new file for your analysis in the `src/analysis/` directory, e.g., `src/analysis/new_analysis.py`. Define the class by extending 
the `Analysis` base class.

```python
from src.analysis.analysis import Analysis

class new_analysis(Analysis):
    def __init__(self, id, name, info, enabled, full_custom_mode, show_images, save_images, save_results, input_interface, output_interface,
                 output_dir, data_selection, custom_params):
        super().__init__(id=id, name=name, info=info, enabled=enabled, full_custom_mode=full_custom_mode, show_images=show_images,
                         save_images=save_images, save_results=save_results, input_interface=input_interface, output_interface=output_interface,
                         output_dir=output_dir, data_selection=data_selection, custom_params=custom_params)

    def check_data(self):
        # Add logic to validate data before analysis
        pass

    def custom_settings(self):
        # Add custom settings logic
        pass

    def run(self):
        """
        # Analysis description
        """
        output_dict = {}
        # Add analysis logic here
        self.results = output_dict
        return
```

---

### 2.3. Create a Configuration File
Add a new entry for your analysis in the `conf/cli/conf_cli_analysis_db.json` file.

```json
{
    "id": 12,
    "name": "new_analysis",
    "info": "Description of the new analysis",
    "enabled": true,
    "full_custom_mode": false,
    "show_images": true,
    "save_images": true,
    "save_results": true,
    "data_selection": {
        "datasets": [],
        "merge_datasets": false,
        "fields": {
            "field_name": null
        }
    },
    "custom_params": {
        "example_param": "value"
    }
}
```

---

### 2.4. Initialize the Analysis
Ensure the `init_analysis` function in `src/analysis/analysis.py` can initialize your new analysis.

```python
if config["name"] == "new_analysis":
    from src.analysis.new_analysis import new_analysis
    analysis = new_analysis(id=config['id'],
                            name=config['name'],
                            info=config['info'],
                            enabled=config['enabled'],
                            full_custom_mode=config['full_custom_mode'],
                            show_images=config['show_images'],
                            save_images=config['save_images'],
                            save_results=config['save_results'],
                            input_interface=input_interface,
                            output_interface=output_interface,
                            output_dir=config['output_dir'],
                            data_selection=config['data_selection'],
                            custom_params=config['custom_params'])
```

### 2.5. Implement the Analysis Logic
Implement the logic for your analysis in the `run` method of your analysis class. This method should contain the core functionality of your 
analysis.

---

## Logging
The service logs its progress using the `logger` utility. Logs include:
- Start and end of the ingestion process.
- Details of each table or dataset being ingested.
- Errors encountered during ingestion.

---

## Error Handling
The service captures exceptions during ingestion and appends error messages to the output. Ensure proper debugging by reviewing logs and error messages.
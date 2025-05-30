import argparse
import os
import json
import subprocess


def start_mlflow_server(backend_store_uri, default_artifact_root, host, port):
    """
    Start the MLflow tracking server.

    :param backend_store_uri: URI of the backend database to store MLflow metadata.
    :param default_artifact_root: Path to store the run artifacts.
    :param host: Host address of the MLflow server.
    :param port: Port of the MLflow server.
    """
    command = (
        f"mlflow server "
        f"--backend-store-uri {backend_store_uri} "
        f"--default-artifact-root {default_artifact_root} "
        f"--host {host} "
        f"--port {port}"
    )

    os.system(command)

    return


if __name__ == "__main__":
    # Read conf file
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', help='configuration file', required=True)

    # Set configuration
    args = arg_parser.parse_args()

    config_file_path = args.c

    config = json.loads(open(config_file_path).read().replace("\n", ""))

    print("Starting mlflow server...")
    start_mlflow_server(backend_store_uri=config['storage_uri'],
                        default_artifact_root=config['storage_uri'],
                        host=config['host'],
                        port=int(config['port']))
    print("Mlflow server stopped.")

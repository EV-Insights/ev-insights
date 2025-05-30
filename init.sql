
-- Connect as superuser
\c postgres

-- Create db
CREATE DATABASE mlflow;
CREATE DATABASE evinsights;

-- Create user
CREATE USER mlflow WITH PASSWORD 'mlflow';
CREATE USER evinsights WITH PASSWORD 'evinsights';

-- Connect as mlflow user to the mlflow database to create the schema and assign permissions
\c mlflow postgres

-- Create mlflow schema
CREATE SCHEMA mlflow AUTHORIZATION mlflow;

-- Assigning permissions to the mlflow user.
GRANT ALL PRIVILEGES ON DATABASE mlflow TO mlflow;
GRANT ALL PRIVILEGES ON SCHEMA mlflow TO mlflow;

-- Connect as evinsights user to the evinsights database to create the schema and assign permissions
\c evinsights postgres

-- Create evinsights schema
CREATE SCHEMA evinsights AUTHORIZATION evinsights;

-- Assigning permissions to the evinsights user
GRANT ALL PRIVILEGES ON DATABASE evinsights TO evinsights;
GRANT ALL PRIVILEGES ON SCHEMA evinsights TO evinsights;
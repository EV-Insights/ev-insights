import os
from pprint import pprint
from fastapi import FastAPI
from src.api.v1.endpoints.analysis import router as analysis_router_v1
from src.api.v1.endpoints.ingestion import router as ingestion_router_v1
from src.api.v1.endpoints.admin import router as admin_router_v1
from src.api.v1.endpoints.forecast import router as forecast_router_v1
# from src.api.v2.endpoints.analysis import router as analysis_router_v2
# from src.api.v2.endpoints.ingestion import router as ingestion_router_v2
# from src.api.v2.endpoints.admin import router as admin_router_v2
# from src.api.v2.endpoints.forecast import router as forecast_router_v2

# Swagger documentation here: http://localhost:<port>/docs#/

# Set conf path
if os.environ["SERVICE_ENVIRONMENT"] == "dev":
    base_conf_folder_path = "conf/api/dev"
elif os.environ["SERVICE_ENVIRONMENT"] == "test":
    base_conf_folder_path = "conf/api/test"
elif os.environ["SERVICE_ENVIRONMENT"] == "prod":
    base_conf_folder_path = "conf/api/prod"
else:
    raise Exception(f"Wrong environment: {os.environ['SERVICE_ENVIRONMENT']}")

app = FastAPI()

# Set base router versions
prefix_base = ""
app.include_router(analysis_router_v1, prefix=prefix_base)
app.include_router(ingestion_router_v1, prefix=prefix_base)
app.include_router(admin_router_v1, prefix=prefix_base)
app.include_router(forecast_router_v1, prefix=prefix_base)

# # Include v1 routers
# prefix_v1 = "/api/v1"
# app.include_router(analysis_router_v1, prefix=prefix_v1)
# app.include_router(ingestion_router_v1, prefix=prefix_v1)
# app.include_router(admin_router_v1, prefix=prefix_v1)
# app.include_router(forecast_router_v1, prefix=prefix_v1)

# Include v2 routers
# prefix_v2 = "/api/v2"
# app.include_router(analysis_router_v2, prefix=prefix_v2)
# app.include_router(ingestion_router_v2, prefix=prefix_v2)
# app.include_router(admin_router_v2, prefix=prefix_v2)
# app.include_router(forecast_router_v2, prefix=prefix_v2)

# Include other router versions if needed
# ...


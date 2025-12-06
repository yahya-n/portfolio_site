from app import app
import os
print(f"DEPLOYMENT_MODE env: {os.getenv('DEPLOYMENT_MODE')}")
print(f"App DEBUG config: {app.config['DEBUG']}")
print(f"App FLASK_ENV config: {app.config.get('FLASK_ENV')}")

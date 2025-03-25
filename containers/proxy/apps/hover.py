import os

# Get all environment variables
env_vars = os.environ

# Write to .env file
with open(".env", "w") as f:
    for key, value in env_vars.items():
        f.write(f'{key}="{value}"\n')

print(".env file has been created with all environment variables.")

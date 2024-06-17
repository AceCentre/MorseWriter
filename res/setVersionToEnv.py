import os

def set_version_env():
    version_file = 'version'
    with open(version_file, 'r') as file:
        version_line = file.readline().strip()
        version_number = version_line.split('=')[1]
        os.environ['APP_VERSION'] = version_number

if __name__ == "__main__":
    set_version_env()
    print(os.environ['APP_VERSION'])  # Just to verify it's set correctly

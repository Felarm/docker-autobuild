import yaml


with open('docker-compose.yml', 'r') as ymlfile:
    docker_config = yaml.full_load(ymlfile)

print(list(docker_config.keys())[0])


for key, value in docker_config.items():
    dicti = docker_config[key]
print(dicti)
print(dicti.get('properties'))
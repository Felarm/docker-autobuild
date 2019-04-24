import yaml
import docker
from sanic import Sanic
from sanic.response import json

app = Sanic()
NUM_WORKERS = 5


@app.route('/start', methods=['POST'])
async def build_and_run_container(request):
    input_file = request.files.get('file')
    with open(input_file.name, 'r') as ymlfile:
        docker_config = yaml.safe_load(ymlfile)
    for key, value in docker_config.items():
        dicti = docker_config[key]
    name = list(docker_config.keys())[0]
    run_params = dicti.get('properties')
    image = run_params.get('image')+':latest'
    command = run_params.get('command')
    ports = run_params.get('port_bindings')[0]
    client = docker.from_env()
    try:
        builded_image = client.images.get(name=image)
    except:
        builded_image = client.images.pull(name=image)
    cont = client.containers.run(name=name, image=builded_image, command=command, ports=ports, detach=True)
    return json({'container id': cont.id})


@app.route('/stop/<int: id>', methods=['POST'])
async def stop_container(request):
    client = docker.from_env()
    id = request.get('id')
    cont = client.containers.get(id)
    cont.stop()
    cont.remove()
    return json({'status': 'stoped and removed'})


@app.route('/list', methods=['GET'])
def list_containers():
    client = docker.from_env()
    return json({'containers': client.containers.list()})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=NUM_WORKERS)

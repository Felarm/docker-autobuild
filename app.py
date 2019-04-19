import yaml
import docker
from sanic import Sanic
from sanic.response import json

app = Sanic()


@app.route('/start', methods=['POST'])
async def run_container(request):
    print(request)
    input_file = request.files.get('file')
    print(input_file.name)
    with open(input_file.name, 'r') as ymlfile:
        docker_config = yaml.safe_load(ymlfile)
    print(docker_config)
    for key, value in docker_config.items():
        dicti = docker_config[key]
    name = list(docker_config.keys())[0]
    run_params = dicti.get('properties')
    image = run_params.get('image')
    command = run_params.get('command')
    ports = run_params.get('port_bindings')[0]
    client = docker.from_env()
    build_image = client.images.pull(image+':latest') #скачивание образа, перенести в отдельный поток
    print('pulled image')
    cont = client.containers.run(name=name, image=build_image, command=command, ports=ports, detach=True)
    print(cont.id)
    print(client.containers.list())
    cont.stop()
    print('container ', cont.id, ' stopped')
    cont.remove()
    print(client.containers.list())
    print(client.images.list())
    client.images.remove(image=image)
    print(client.images.list())
    return json({'container id': cont.id})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=4)

import yaml
import docker
from sanic import Sanic
from sanic.response import json
import concurrent.futures
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = Sanic()


async def build_container(image):
    print('in build_container')
    import json
    cli = docker.APIClient()
    #for line in cli.pull(image, stream=True, decode=True):
    #    await print(line['status'])
    cli.pull(image, stream=True, decode=True)
    cli = docker.from_env()
    return cli.images.get(name=image)
        #print(json.dumps(line, indent=4)['status'])



@app.route('/start', methods=['POST'])
async def run_container(request):
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
        print('in try')
        builded_image = client.images.get(name=image)
    except:
        print('in exception')
        builded_image = await build_container(image)

    cont = client.containers.run(name=name, image=builded_image, command=command, ports=ports, detach=True)

    print('container id: ', cont.id)
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
    #pool = ThreadPoolExecutor()
    app.run(host='0.0.0.0', port=8000, workers=4)

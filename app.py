import yaml
import docker
from sanic import Sanic
from sanic.response import json

app = Sanic()
app_settings = {
    'NUM_WORKERS': 5,
    'HOST': '0.0.0.0',
    'PORT': 8000
}  # параметры запуска сервера
app.config.update(app_settings)  # добавление в настройки приложения параметров для его запуска
client = docker.from_env()  # инициализация клиента для обращения к docker


@app.route('/start', methods=['POST'])
async def build_and_run_container(request):
    """
    Функция считывает файл из POST запроса и выбирает из него параметры:
    name - строка, название контейнера;
    run_params - словарь, параметры контейнера, куда входят:
        image - строка, название изображения, на основе которого собирается контейнер, по-умолчанию используется
        последняя версия
        command - строка, команды, которые исполняются после запуска контейнера
        ports - порты, используемые в контейнере
    Затем локально ищется образ, в случае его остуствия исполняется команда-аналог docker pull. Это - блокирующий
    метод. С блокировкой поможет справится увеличение количества потоков во время запуска сервера.
    Затем исполняется команда-аналог docker run, куда задаются считанные параметры. В случае наличия контейнера с таким
    же имененм - возвращается json ответ с текстом ошибки.
    После построения и запуска контейнера - функция возвращает json-ответ с id этого контейнера
    """
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
    try:
        builded_image = client.images.get(name=image)
    except docker.errors.ImageNotFound:
        builded_image = client.images.pull(name=image)
    try:
        cont = client.containers.run(name=name, image=builded_image, command=command, ports=ports, detach=True)
    except docker.errors.APIError as err:
        return json({'error': str(err.explanation)})
    return json({'container id': cont.id})


@app.route('/stop/<cont_id>', methods=['POST'])
async def stop_container(request, cont_id):
    """
    Функция принимает id контейнера, останавливает, затем удаляет его
    Возвращает json-ответ с id контейнера, который был удален
    """
    cont = client.containers.get(cont_id)
    cont.stop()
    cont.remove()
    return json({cont_id: 'stoped and removed'})


@app.route('/list', methods=['GET'])
def list_containers(request):
    """
    Функция возвращает список активных контейнеров.
    """
    containers = client.containers.list()  # для отображения всех контейнеров следует установить параметр all=True
    output = {}
    for cont in containers:
        output[cont.name] = {'CONTAINER ID': cont.id,
                             'IMAGE': cont.attrs.get('Image'),
                             'COMMAND': cont.attrs.get('Config').get('Cmd'),
                             'CREATED': cont.attrs.get('Created'),
                             'STATUS': cont.attrs.get('State').get('Status'),
                             'PORTS': cont.attrs.get('HostConfig').get('PortBindings'),
                             }
    return json({'containers': output})


if __name__ == '__main__':
    app.run(host=app.config.HOST, port=app.config.PORT, workers=app.config.NUM_WORKERS)

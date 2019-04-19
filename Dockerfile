FROM alpine:3.5

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

COPY requirements.txt /usr/src/app/

RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY views.py /usr/src/app/
COPY tasks.py /usr/src/app/
COPY worker.py /usr/src/app/
COPY send_mail.py /usr/src/app/

EXPOSE 5000

ENV FLASK_APP=/usr/src/app/views.py
CMD ["python", "/usr/src/app/worker.py"]
CMD ["flask", "run", "--host", "0.0.0.0"]


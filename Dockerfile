FROM python:3.6-slim-buster
WORKDIR /app
COPY . .
RUN pip install -r hello-kube-py_req.txt
EXPOSE 3000
CMD ["python", "hello-kube.py"]

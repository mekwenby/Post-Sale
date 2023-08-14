FROM python:3.10.12
COPY . /App
WORKDIR /App
RUN pip3 install -r requirements.txt -i "http://mirrors.aliyun.com/pypi/simple" --trusted-host "mirrors.aliyun.com"
EXPOSE 8080
CMD python run.py
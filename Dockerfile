FROM python:3.10.8
COPY . /App
WORKDIR /App
RUN pip3 install -r requirements.txt -i "http://mirrors.aliyun.com/pypi/simple" --trusted-host "mirrors.aliyun.com"
EXPOSE 12309
CMD uwsgi --ini uwsgi.ini
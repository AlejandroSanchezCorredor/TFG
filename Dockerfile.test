FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt ./

COPY application ./application

RUN pip install -r requirements.txt

CMD ["application.handler.scheduler"]

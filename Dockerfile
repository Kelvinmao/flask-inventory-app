FROM python:3.8
WORKDIR /Inventory

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . .
EXPOSE 5005
CMD ["gunicorn", "run:app", "-c", "./gunicorn.conf.py"]
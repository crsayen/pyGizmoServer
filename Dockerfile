FROM python:3.7
COPY . /app
WORKDIR /app
RUN apt-get update || : && apt-get install npm -y
RUN pip install ./
RUN npm install
RUN npm run build
EXPOSE 36364
EXPOSE 11111
CMD ["python", "pyGizmoServer/run.py", "example"]
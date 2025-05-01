# Python 3.12 image
FROM python:3.12-slim

# PostgreSQL üçün libpq-dev quraşdırırıq
RUN apt-get update && apt-get install -y libpq-dev

# Curl və ping alətlərini quraşdırmaq
RUN apt-get update && apt-get install -y curl iputils-ping

# Layihə qovluğunu təyin edirik
WORKDIR /app

# requirements faylını kopyalayırıq
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Bütün faylları konteynerə kopyalayırıq
COPY . /app/

# manage.py faylı /app/restora_project içindədir, ora keçib collectstatic işlədirik
WORKDIR /app/restora_project
RUN python manage.py collectstatic --noinput

# Gunicorn ilə serveri işə salırıq
CMD ["gunicorn", "restora_project.wsgi:application", "--bind", "0.0.0.0:8000"]

FROM python:3.8-slim-buster

COPY . .

# Настройка прокси
ENV http_proxy=http://79.174.91.58:8080
ENV https_proxy=http://79.174.91.58:8080

# Установка pip
RUN python3 -m ensurepip && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade setuptools wheel

# Настройка PyPI
RUN pip3 config set global.use_new_style_url True && \
    pip3 config set pypi.pypi.org https://pypi.tuna.tsinghua.edu.cn/simple

# Установка зависимостей
RUN pip3 install --no-cache-dir -r requirements.txt --timeout=300 && \
    pip3 install --no-cache-dir -r requirements.txt --timeout=300

# Команда запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

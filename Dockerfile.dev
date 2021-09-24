
# Base Image for builder
FROM python:3.9 as builder

# Install Requirements
COPY requirements.txt /
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt


# Build the app image
FROM python:3.9

# Create directory for the app user
RUN mkdir -p /home/app

# Create the app user
RUN groupadd app && useradd -g app app

# Create the home directory
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Install Requirements
COPY --from=builder /wheels /wheels
COPY --from=builder requirements.txt .
RUN pip install --no-cache /wheels/*

COPY . $APP_HOME

RUN chown -R app:app $APP_HOME

USER app

CMD ["uvicorn", "project_name.app:app", "--host=0.0.0.0","--port=8000","--reload"]

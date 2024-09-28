FROM python:3.12

ENV APP_HOME /app

# Set the working directory
WORKDIR $APP_HOME

# Copy the current directory contents into the container at /app
COPY app .

# Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 3000

ENTRYPOINT ["python", "main.py"]
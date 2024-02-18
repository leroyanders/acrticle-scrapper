# Use the official Python image with version 3.12.2 as the base image
FROM python:3.12.2

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Create a virtual environment and activate it
RUN python3 -m venv env && . env/bin/activate

# Install any needed packages specified in requirements.txt
RUN /bin/bash -c "source env/bin/activate && pip install -r requirements.txt"

# Run the setup script (assuming this installs nltk with punkt)
RUN /bin/bash -c "source env/bin/activate && python setup.py"

# Command to run the server
CMD /bin/bash -c "source env/bin/activate && python main.py"

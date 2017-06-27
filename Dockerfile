FROM python:latest

MAINTAINER Caesar Kabalan <caesar.kabalan@gmail.com>

# Copy the code into the container
COPY . /cs/clientdiscord/

# Upgrade pip
RUN pip install --upgrade pip

# Install prereqs with pip
RUN pip install -r /cs/clientdiscord/requirements.txt

# Set the entrypoint to run the main method
CMD [ "python", "/cs/clientdiscord/__main__.py" ]

FROM telegraf:1.29-alpine

# Switch to root user to install packages
USER root

# Install Python
RUN apk update && apk add --no-cache python3

# Copy the parser script and its dependencies into the image
COPY f1_24_telemetry_parser.py /f1_24_telemetry_parser.py
COPY packets /packets

# Switch back to the default telegraf user
USER telegraf 
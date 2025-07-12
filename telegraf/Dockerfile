FROM telegraf:1.29

# Switch to root to install packages
USER root

# Install Python using apt-get
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to the telegraf user for security
USER telegraf 
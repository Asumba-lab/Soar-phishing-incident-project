FROM python:3.11-slim

# Install tini for proper PID 1 and signal handling and ca-certificates
RUN apt-get update \
	&& apt-get install -y --no-install-recommends tini ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app

# Create a non-root user and secure file permissions
RUN groupadd --system app && useradd --system --create-home --gid app appuser \
	&& mkdir -p /app/logs \
	&& chown -R appuser:app /app \
	&& chmod -R 750 /app

USER appuser

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "playbook_demo.py"]

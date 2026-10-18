# Use minimal Python 3.12 Alpine image (~45MB)
FROM python:3.12-alpine

# Set metadata labels
LABEL maintainer="duytrancoder" \
      description="Resilient DevOps Log Analyzer CLI"

# Create a non-root group and user for security best practices
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set working directory and grant appuser ownership
WORKDIR /app
RUN chown -R appuser:appgroup /app

# Copy application script and adjust permissions
COPY --chown=appuser:appgroup log_analyzer.py .

# Switch to non-root user
USER appuser

# Configure container as a CLI tool
ENTRYPOINT ["python", "log_analyzer.py"]

# Default action when no arguments provided: show help
CMD ["--help"]

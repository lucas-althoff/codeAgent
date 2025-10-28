FROM postgres:16.3

# Install necessary packages including build tools for pgvector
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*

# Clone and install pgvector
RUN git clone --branch v0.7.0 https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && cd /tmp/pgvector \
    && make \
    && make install \
    && rm -rf /tmp/pgvector
    
# Set environment variables for PostgreSQL
ENV POSTGRES_DB=codeAgent
ENV POSTGRES_USER=mirante
ENV POSTGRES_PASSWORD=mirante2025pass

# Initialization SQL script and all migration files
COPY db-init.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/db-init.sh

# Expose PostgreSQL port
EXPOSE 5432

CMD ["postgres"]
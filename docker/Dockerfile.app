FROM python:3.11-slim AS base

# Set work directory
WORKDIR /code

# Copy project files
COPY . /code

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir fastapi uvicorn streamlit pandas plotly requests

# Expose API and Streamlit ports
EXPOSE 8000
EXPOSE 8501

# Start both API (simple) and Streamlit
CMD ["/bin/bash", "-c", "python api_simple.py & streamlit run app/Home.py --server.port 8501 --server.headless true --server.address 0.0.0.0"]
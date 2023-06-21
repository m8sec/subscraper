# Dockerfile for m8sec/subscraper

FROM python:3

LABEL org.label-schema.name="subscraper" \
    org.label-schema.description="Subdomain Enumeration Tool" \
    org.label-schema.vcs-url="https://github.com/m8sec/subscraper"

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python","/app/subscraper.py"]
CMD ["--help"]
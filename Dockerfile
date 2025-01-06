FROM python:3.12-slim

COPY ./ ./

EXPOSE 8888

ENTRYPOINT ["python"]
CMD ["./src/http_server.py"]

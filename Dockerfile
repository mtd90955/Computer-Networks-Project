From ubuntu:22.10

WORKDIR /home

COPY server .
COPY client .

CMD ["bash"]

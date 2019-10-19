FROM continuumio/miniconda:4.7.10

RUN apt-get -y update && apt-get install -y --no-install-recommends \
         wget \
         nginx \
    && rm -rf /var/lib/apt/lists/*

ADD requirements.yml ./tmp/requirements.yml
# RUN while read requirement; do conda install --yes $requirement; done < ./tmp/requirements.txt
RUN conda env update -n base --file ./tmp/requirements.yml

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

# Set up the program in the image
COPY random-forest /opt/program
WORKDIR /opt/program
# https://medium.com/@chadlagore/conda-environments-with-docker-82cdc9d25754
# Use pycloud.env.yml and auto activate

FROM continuumio/miniconda:4.7.10

ADD pycloud.env.yml ./tmp/environment.yml
RUN conda env create -f /tmp/environment.yml

# Pull the environment name out of the environment.yml
RUN echo "source activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)" > ~/.bashrc
ENV PATH /opt/conda/envs/$(head -1 /tmp/environment.yml | cut -d' ' -f2)/bin:$PATH

WORKDIR /var/app

COPY malware /var/app/malware
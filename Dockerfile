FROM python:3.9.17-slim-bullseye

# define python environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system base packages
RUN apt-get update && apt-get install -y ncbi-blast+ nano curl git wget zip unzip gnupg libglib2.0-0 libnss3 \
    && git config --global --add safe.directory /home/biopep

# install miniconda
ENV PATH "/root/miniconda/bin:${PATH}"
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -b -p /root/miniconda \
    && rm /tmp/miniconda.sh \
    && conda update conda \
    && conda config --set auto_activate_base false

# download the Chrome Browser
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update -y \
    && apt-get install -y google-chrome-stable

# download the Chrome Driver
RUN CHROME_VERSION=$(google-chrome --version | grep -o '[0-9.]*') \
    && wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver.zip chromedriver-linux64/chromedriver -d /usr/local/bin/

# set display port as an environment variable
ENV DISPLAY=:99

# download Protein Data Bank (PDB) AND make blastdb
RUN wget https://s3.rcsb.org/pub/pdb/derived_data/pdb_seqres.txt.gz \
    && gzip -d pdb_seqres.txt.gz \
    && mkdir blastdb \
    && mv pdb_seqres.txt /blastdb/pdb_seqres.fasta \
    && makeblastdb -in /blastdb/pdb_seqres.fasta -dbtype prot -out /blastdb/pdb_seqres

# setup workdir
WORKDIR /home/biopep
COPY . .

# create environment
RUN conda create --name biopep-env --file conda-linux-64.lock \
    && eval "$(conda shell.bash hook)" \
    && conda activate biopep-env \
    && sed -i "s/license = r'XXXX'/import os/g" ${CONDA_PREFIX}/lib/modeller-10.4/modlib/modeller/config.py \
    && echo "license = os.environ.get('KEY_MODELLER')" >> ${CONDA_PREFIX}/lib/modeller-10.4/modlib/modeller/config.py \
    && poetry install   

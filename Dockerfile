from kaldiasr/kaldi

ADD . /language-model-service

RUN apt update
RUN apt install -y \
  software-properties-common

RUN wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tar.xz
RUN tar xvf Python-3.6.1.tar.xz

RUN apt update
RUN apt install -y \
  graphviz \
  libreadline-gplv2-dev \
  libncursesw5-dev \
  libssl-dev \
  libsqlite3-dev \
  tk-dev \
  libgdbm-dev \
  libc6-dev \
  libbz2-dev

WORKDIR Python-3.6.1

RUN ./configure
RUN make
RUN make install


RUN cp /language-model-service/service/Makefile /opt/kaldi/src/bin/Makefile
RUN cp /language-model-service/service/decode-faster-service.cc /opt/kaldi/src/bin/decode-faster-service.cc

WORKDIR /opt/kaldi/src/bin/
RUN make
RUN ./decode-faster-service \
    --beam=13 \
    --acoustic-scale=2.21 \
    --word-symbol-table=/language-model-service/data/words.txt \
    --model=/language-model-service/data/TLG9.fst \
    --input-folder=/tmp/ \
    --output-folder=/tmp/

WORKDIR /language-model-service
RUN mkdir -p /language-model-service/Logs

RUN pip3.6 install \
  celery==4.1.1 \
  redis==3.2.0 \
  requests==2.13.0 \
  numpy==1.16.4

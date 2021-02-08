FROM python:3.7
LABEL author="Lucien ZUBER <https://github.com/LucienZuber>"

WORKDIR /app

# TA-Lib
RUN wget https://artiya4u.keybase.pub/TA-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install
RUN rm -R ta-lib ta-lib-0.4.0-src.tar.gz

# install python requirements
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Run application
COPY . .
CMD [ "python", "./main.py" ]
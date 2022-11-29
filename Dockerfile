ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-slim

# configure apt to install minimal dependencies in non-interactive mode.
ENV DEBIAN_FRONTEND noninteractive
RUN echo 'APT::Install-Recommends "false";' >> /etc/apt/apt.conf; \
    echo 'APT::Install-Suggests "false";' >> /etc/apt/apt.conf

RUN \
    export MYSQL_CONNECTOR='mysql-connector-odbc-8.0.31-linux-glibc2.27-x86-64bit' \
    && apt-get update && apt-get install -y \
    unixodbc-dev unixodbc \
    wget libtool build-essential g++ \
    odbc-postgresql \
    libsqlite3-dev \
    libsqliteodbc \
    && wget https://dev.mysql.com/get/Downloads/Connector-ODBC/8.0/${MYSQL_CONNECTOR}.tar.gz \
    && tar xvzf ${MYSQL_CONNECTOR}.tar.gz \
    && cp ${MYSQL_CONNECTOR}/bin/* /usr/bin/. \
    && cp ${MYSQL_CONNECTOR}/lib/lib* /usr/local/lib/. \
    && myodbc-installer -a -d -n "MySQL ODBC 8.0 Driver" -t "Driver=/usr/local/lib/libmyodbc8w.so" \
    && myodbc-installer -a -d -n "MySQL ODBC 8.0" -t "Driver=/usr/local/lib/libmyodbc8a.so" \
    && rm -rf ${MYSQL_CONNECTOR}* \
    && apt-get autoremove -y

WORKDIR /aioodbc
COPY requirements-dev.txt .
RUN pip install -U pip setuptools && \
    pip install -r requirements-dev.txt

COPY . .
RUN pip install -e .

WORKDIR /aioodbc

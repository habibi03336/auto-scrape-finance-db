FROM alpine
RUN \
    apk update && \
    apk add py3-pip && \
    pip install python-dotenv && \
    apk add git && \
    git clone https://github.com/habibi03336/dart-scraper.git && \
    cd dart-scraper && \
    pip install -r requirements.txt && \
    pip install . && \
    cd /etc && \
    echo > entrypoint.sh '#!/bin/bash' && \
    echo >> entrypoint.sh 'cd ../dart-scraper' && \
    echo >> entrypoint.sh 'git pull' && \
    echo >> entrypoint.sh 'pip install --root-user-action=ignore .' && \
    echo >> entrypoint.sh 'exec "$@"' && \
    chmod a+x entrypoint.sh

ENTRYPOINT ["sh", "/etc/entrypoint.sh"]
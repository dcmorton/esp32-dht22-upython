FROM dcmorton/esp32-micropython-image-builder:latest

COPY configmgr.py ${MICROPYTHON}/ports/esp32/modules
COPY main.py ${MICROPYTHON}/ports/esp32/modules
COPY wifimgr.py ${MICROPYTHON}/ports/esp32/modules

WORKDIR ${MICROPYTHON}/ports/esp32

ENTRYPOINT ["make", "PYTHON=python"]

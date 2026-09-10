FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254
RUN pip install --no-cache-dir --disable-pip-version-check 'psycopg[binary]==3.3.5' 'typing-extensions==4.16.0' 'aiohttp==3.14.3' \
    && useradd --uid 10004 --gid 26 --no-create-home --shell /usr/sbin/nologin ai_lan_status
COPY infrastructure/postgres/build/runtime_guard.so /usr/local/lib/ai-invest/runtime_guard.so
COPY backend/ai_invest_core/__init__.py /opt/ai-invest/backend/ai_invest_core/__init__.py
COPY backend/ai_invest_core/lan_app.py /opt/ai-invest/backend/ai_invest_core/lan_app.py
COPY frontend/lan /opt/ai-invest/frontend/lan
COPY scripts/lan_v0.py /opt/ai-invest/scripts/lan_v0.py
RUN chmod 0444 /usr/local/lib/ai-invest/runtime_guard.so
USER 10004:26
ENV LD_PRELOAD=/usr/local/lib/ai-invest/runtime_guard.so
ENTRYPOINT ["/usr/local/bin/python3","-I","-B","/opt/ai-invest/scripts/lan_v0.py"]

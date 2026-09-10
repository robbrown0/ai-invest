FROM percona/percona-distribution-postgresql@sha256:d37e949abdbb4f8b1e0ea2cb6961dd70dcba13738c05142978f616da835a79a8
USER 0
RUN useradd --uid 10001 --gid 26 --no-create-home --shell /sbin/nologin ai_tenant_a && useradd --uid 10002 --gid 26 --no-create-home --shell /sbin/nologin ai_tenant_b
COPY build/runtime_guard.so /usr/local/lib/ai-invest/runtime_guard.so
COPY build/guard_probe /usr/local/bin/ai-invest-guard-probe
COPY bootstrap.py /opt/ai-invest/bootstrap.py
RUN chmod 0555 /usr/local/bin/ai-invest-guard-probe && chmod 0444 /usr/local/lib/ai-invest/runtime_guard.so
USER 26:26
ENV LD_PRELOAD=/usr/local/lib/ai-invest/runtime_guard.so

"""
This addon logs TLS interception success/failure as line-delimited JSON.

Example:

    > mitmdump -s tlslogger.py --set tls_logfile=tls-log.txt --set tls_tag=foo.apk

"""
from __future__ import annotations
from mitmproxy import ctx, tls
import json
import time

def load(l):
    l.add_option(
        "tls_logfile", str, "",
        "Log file for TLS success/failure",
    )
    l.add_option(
        "tls_app", str, "",
        "Inspected app",
    )
    l.add_option(
        "tls_method", str, "",
        "Inspection method",
    )
    l.add_option(
        "tls_device", str, "",
        "Inspection device",
    )
    l.add_option(
        "tls_downloadgroup", str, "",
        "Inspection group",
    )

t_start = time.time()

def log_result(data: tls.TlsData, success: bool) -> None:
    result = json.dumps({
        "version": 2,
        "timestamp": t_start,
        "sni": data.context.server.sni,
        "success": success,
        "peername": data.context.server.peername,
        "app": ctx.options.tls_app,
        "method": ctx.options.tls_method,
        "device": ctx.options.tls_device,
        "group": ctx.options.tls_downloadgroup,

    })
    if ctx.options.tls_logfile:
        with open(ctx.options.tls_logfile,"a") as f:
            f.write(f"{result}\n")
    else:
        ctx.log.warn(f"{data.context.client.peername} {result}")


def tls_established_client(data: tls.TlsData):
    log_result(data, True)

def tls_failed_client(data: tls.TlsData):
    log_result(data, False)
import json
import logging

import click

# Heavily inspired on https://github.com/click-contrib/click-log/blob/master/click_log/core.py


class JsonEncoder(json.JSONEncoder):
    """
    A custom encoder extending the default JSONEncoder
    """

    def default(self, obj):
        try:
            return super(JsonEncoder, self).default(obj)
        except TypeError:
            try:
                return str(obj)
            except Exception:
                return None


class ColorFormatter(logging.Formatter):
    colors = {
        "error": dict(fg="red"),
        "exception": dict(fg="red"),
        "critical": dict(fg="red"),
        "debug": dict(fg="blue"),
        "warning": dict(fg="yellow"),
        "info": dict(fg="blue"),
    }

    def format(self, record):
        if not record.exc_info:
            level = record.levelname.lower()
            msg = record.getMessage()
            if level in self.colors:
                prefix = click.style("{}: ".format(level), **self.colors[level])
                msg = "\n".join(prefix + x for x in msg.splitlines())
            if hasattr(record, "extra_log_attributes"):
                msg += " --- " + json.dumps(
                    record.extra_log_attributes, cls=JsonEncoder
                )
            return msg
        return super().format(record)


class ClickHandler(logging.Handler):
    _use_stderr = True
    formatter = ColorFormatter()

    def emit(self, record):
        try:
            msg = self.format(record)
            click.echo(msg, err=self._use_stderr)
        except Exception:
            self.handleError(record)


def configure_logger(logger):
    ch = ClickHandler()
    ch.setFormatter(ColorFormatter())
    logger.addHandler(ch)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
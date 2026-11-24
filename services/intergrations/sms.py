from flask import current_app


def send_sms(to, message):
    provider = current_app.config["SMS_PROVIDER"]
    if provider == "console":
        current_app.logger.info("SMS -> %s: %s", to, message)
        return True
    raise RuntimeError(f"SMS provider {provider} not implemented")

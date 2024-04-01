from flask import current_app, session, request, url_for
from cas import CASClient


def generate_session():
    """ Send the user to Rice CAS to establish a new session.
    """
    cas_client = CASClient(
        version=current_app.config['CAS_CLIENT_VERSION'],
        service_url=current_app.config['CAS_SERVICE_URL'],
        server_url=current_app.config['CAS_SERVER_URL']
    )

    next = request.args.get('next')
    ticket = request.args.get('ticket')
    if not ticket:
        cas_login_url = cas_client.get_login_url()
        current_app.logger.debug('CAS login URL: %s', cas_login_url)
        return cas_login_url

    current_app.logger.debug('ticket: %s', ticket)
    current_app.logger.debug('next: %s', next)

    user, attributes, pgtiou = cas_client.verify_ticket(ticket)

    current_app.logger.debug(
        'CAS verify ticket response: user: %s, attributes: %s, pgtiou: %s',
        user, attributes, pgtiou
    )

    if not user:
        return url_for('index')
    else:
        session['username'] = user
        return url_for('index')


def kill_session():
    """ Destroy the user session.
    """
    cas_client = CASClient(
        version=current_app.config['CAS_CLIENT_VERSION'],
        service_url=current_app.config['CAS_SERVICE_URL'],
        server_url=current_app.config['CAS_SERVER_URL']
    )

    session.pop('username', None)
    current_app.logger.debug('Killing session')

    redirect_url = url_for('logout_callback', _external=True)
    cas_logout_url = cas_client.get_logout_url(redirect_url)
    current_app.logger.debug('CAS logout URL: %s', cas_logout_url)

    return cas_logout_url

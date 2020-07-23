from urllib import parse
import json
import hmac
import hashlib
from bravado.client import (
    construct_request,
    ResourceDecorator as BaseResourceDecorator,
    CallableOperation as BaseCallableOperation,
    SwaggerClient as BaseSwaggerClient
)
from bravado.requests_client import RequestsClient
from bravado.warning import warn_for_deprecated_op
from bravado.config import RequestConfig
from BitMEXAPIKeyAuthenticator import APIKeyAuthenticator as BaseAPIKeyAuthenticator


class APIKeyAuthenticator(BaseAPIKeyAuthenticator):

    def apply(self, r):
        if not self.api_key or not self.api_secret:
            r.headers.pop('api-expires', None)
            r.headers.pop('api-key', None)
            r.headers.pop('api-signature', None)
            return r
        return super().apply(r)


class CallableOperation(BaseCallableOperation):

    def __call__(self, **op_kwargs):
        """Invoke the actual HTTP request and return a future.

        :rtype: :class:`bravado.http_future.HTTPFuture`
        """
        warn_for_deprecated_op(self.operation)

        http_client = self.operation.swagger_spec.http_client
        setattr(http_client, 'authenticator', op_kwargs.pop('authenticator', None))
        # Get per-request config
        request_options = op_kwargs.pop('_request_options', {})
        request_config = RequestConfig(request_options, self.also_return_response)

        request_params = construct_request(
            self.operation, request_options, **op_kwargs)
        return http_client.request(
            request_params,
            operation=self.operation,
            request_config=request_config,
        )


class ResourceDecorator(BaseResourceDecorator):

    def __getattr__(self, name):
        """
        :rtype: :class:`CallableOperation`
        """
        return CallableOperation(getattr(self.resource, name), self.also_return_response)


class SwaggerClient(BaseSwaggerClient):

    def _get_resource(self, item):
        """
        :param item: name of the resource to return
        :return: :class:`Resource`
        """
        resource = self.swagger_spec.resources.get(item)
        if not resource:
            raise AttributeError(
                'Resource {0} not found. Available resources: {1}'
                .format(item, ', '.join(dir(self))))

        # Wrap bravado-core's Resource and Operation objects in order to
        # execute a service call via the http_client.
        return ResourceDecorator(resource, self.__also_return_response)


def bitmex_connector(test=True, config=None, api_key=None, api_secret=None):
    if config is None:
        # See full config options at http://bravado.readthedocs.io/en/latest/configuration.html
        config = {
            # Don't use models (Python classes) instead of dicts for #/definitions/{models}
            'use_models': False,
            # bravado has some issues with nullable fields
            'validate_responses': False,
            # Returns response in 2-tuple of (body, response); if False, will only return body
            'also_return_response': True,
        }

    if test:
        host = 'https://testnet.bitmex.com'
    else:
        host = 'https://www.bitmex.com'

    spec_uri = host + '/api/explorer/swagger.json'

    request_client = RequestsClient()
    request_client.authenticator = APIKeyAuthenticator(host, api_key, api_secret)
    return SwaggerClient.from_url(spec_uri, config=config, http_client=request_client)


# Generates an API signature.
# A signature is HMAC_SHA256(secret, verb + path + nonce + data), hex encoded.
# Verb must be uppercased, url is relative, nonce must be an increasing 64-bit integer
# and the data, if present, must be JSON without whitespace between keys.
def bitmex_signature(api_secret, verb, url, nonce, postdict=None):
    """Given an API secret key and data, create a BitMEX-compatible signature."""
    data = ''
    if postdict:
        # separators remove spaces from json
        # BitMEX expects signatures from JSON built without spaces
        data = json.dumps(postdict, separators=(',', ':'))
    parsed_url = parse.urlparse(url)
    path = parsed_url.path
    if parsed_url.query:
        path = path + '?' + parsed_url.query
    message = (verb + path + str(nonce) + data).encode('utf-8')
    signature = hmac.new(api_secret.encode('utf-8'), message, digestmod=hashlib.sha256).hexdigest()
    return signature

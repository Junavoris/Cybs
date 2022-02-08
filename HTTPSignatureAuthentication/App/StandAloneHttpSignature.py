import json
import hashlib
import base64
import ssl
import urllib3
import re
import hmac
import warnings

from datetime import date, datetime
from time import mktime
from wsgiref.handlers import format_date_time
from six import PY3, integer_types, iteritems, text_type

class StandAloneHttpSignature:
    def get_time(self):
        now = datetime.now()
        stamp = mktime(now.timetuple())

        return format_date_time(stamp)
        
    def __init__(self, payload):
        warnings.filterwarnings("ignore", category=DeprecationWarning) 
        self.request_host = "apitest.cybersource.com"
        self.merchant_id = "junavoris"
        self.merchant_key_id = "bf304971-faf3-4cb9-b276-43cbfd6e3d3d"
        self.merchant_secret_key = "MPDkeqMxsEi7T0cbk37GvuS+SJYygr6X8cBqjGelW4U="
        
        # REQUEST PAYLOAD
        self.payload = payload

        self.pool_manager = urllib3.PoolManager(
                num_pools=4,
                maxsize=4,
                cert_reqs=ssl.CERT_REQUIRED,
                ca_certs=None,
                cert_file=None,
                key_file=None
            )
            
        self.PRIMITIVE_TYPES = (float, bool, bytes, text_type) + integer_types
        self.NATIVE_TYPES_MAPPING = {
            'int': int,
            'long': int if PY3 else long,
            'float': float,
            'str': str,
            'bool': bool,
            'date': date,
            'datetime': datetime,
            'object': object,
        }

    def sanitize_for_serialization(self, obj):
        """
        Builds a JSON POST object.
        If obj is None, return None.
        If obj is str, int, long, float, bool, return directly.
        If obj is datetime.datetime, datetime.date
            convert to string in iso8601 format.
        If obj is list, sanitize each element in the list.
        If obj is dict, return the dict.
        If obj is swagger model, return the properties dict.
        :param obj: The data to serialize.
        :return: The serialized form of data.
        """
        if obj is None:
            return None
        elif isinstance(obj, self.PRIMITIVE_TYPES):
            return obj
        elif isinstance(obj, list):
            return [self.sanitize_for_serialization(sub_obj)
                    for sub_obj in obj]
        elif isinstance(obj, tuple):
            return tuple(self.sanitize_for_serialization(sub_obj)
                         for sub_obj in obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()

        if isinstance(obj, dict):
            obj_dict = obj
        else:
            # Convert model obj to dict except
            # attributes `swagger_types`, `attribute_map`
            # and attributes which value is not None.
            # Convert attribute name to json key in
            # model definition for request.
            obj_dict = {obj.attribute_map[attr]: getattr(obj, attr)
                        for attr, _ in iteritems(obj.swagger_types)
                        if getattr(obj, attr) is not None}

        return {key: self.sanitize_for_serialization(val)
                for key, val in iteritems(obj_dict)}

    def parameters_to_tuples(self, params, collection_formats):
        """
        Get parameters as list of tuples, formatting collections.
        :param params: Parameters as dict or list of two-tuples
        :param dict collection_formats: Parameter collection formats
        :return: Parameters as list of tuples, collections formatted
        """
        new_params = []
        if collection_formats is None:
            collection_formats = {}
        for k, v in iteritems(params) if isinstance(params, dict) else params:
            if k in collection_formats:
                collection_format = collection_formats[k]
                if collection_format == 'multi':
                    new_params.extend((k, value) for value in v)
                else:
                    if collection_format == 'ssv':
                        delimiter = ' '
                    elif collection_format == 'tsv':
                        delimiter = '\t'
                    elif collection_format == 'pipes':
                        delimiter = '|'
                    else:  # csv is the default
                        delimiter = ','
                    new_params.append(
                        (k, delimiter.join(str(value) for value in v)))
            else:
                new_params.append((k, v))
        return new_params

    def get_digest(self):
        hashobj = hashlib.sha256()
        hashobj.update(self.payload.encode('utf-8'))
        hash_data = hashobj.digest()
        digest = base64.b64encode(hash_data)

        return digest

    def get_signature(self, method, resource, time):
        # Getting HTTP Signature
        header_list = ([])

        # Key id is the key obtained from EBC
        header_list.append("keyid=\"" + str(self.merchant_key_id) + "\"")
        header_list.append(", algorithm=\"HmacSHA256\"")

        if method.upper() == 'POST':
            postheaders = "host date (request-target) digest v-c-merchant-id"
            header_list.append(", headers=\"" + postheaders + "\"")
        else:
            getheaders = "host date (request-target) v-c-merchant-id"
            header_list.append(", headers=\"" + getheaders + "\"")

        signature_list = ([])

        # This method adds the host header
        signature_list.append("host: " + self.request_host + "\n")

        # This method adds the date header
        signature_list.append("date: " + time + "\n")

        # This method adds the request target
        signature_list.append("(request-target): ")

        request_target = method + " " + resource
        signature_list.append(request_target + "\n")

        # This method returns digest value which is SHA-256 hash of the payload which is BASE-64 Encoded
        if method.upper() == 'POST':
            digest = self.get_digest()

            # This method adds the digest header only for post
            signature_list.append("digest: SHA-256=" + digest.decode("utf-8") + "\n")

        # This method adds the v-c-merchant-id header
        signature_list.append("v-c-merchant-id: " + self.merchant_id)

        sig_value = "".join(signature_list)

        sig_value_string = str(sig_value)
        sig_value_utf = bytes(sig_value_string, encoding='utf-8')

        secret = base64.b64decode(self.merchant_secret_key)

        hash_value = hmac.new(secret, sig_value_utf, hashlib.sha256)

        signature = base64.b64encode(hash_value.digest()).decode("utf-8")

        header_list.append(", signature=\"" + signature + "\"")
        token = ''.join(header_list)

        return token

    def process_post(self, rsrc):
        resource = rsrc
        method = 'post'

        time = self.get_time()

        token = self.get_signature(method, resource, time)

        header_params = {}
        header_params['Accept'] = 'application/hal+json;charset=utf-8'
        header_params['Content-Type'] = 'application/json;charset=utf-8'
        header_params['Accept-Encoding'] = '*'
        header_params['v-c-merchant-id'] = self.merchant_id
        header_params["Date"] = time
        header_params["Host"] = self.request_host
        header_params["User-Agent"] = "Mozilla/5.0"

        # Only required for POST request
        digest = self.get_digest()
        header_params["Digest"] = "SHA-256=" + digest.decode("utf-8")

        header_params["Signature"] = token

        header_params = self.sanitize_for_serialization(header_params)
        header_params = dict(self.parameters_to_tuples(header_params, None))

        # Only required for POST request
        body = self.sanitize_for_serialization(self.payload)

        url = "https://" + self.request_host + resource

        # print("\n -- RequestURL -- ")
        # print("\tURL : " + url)
        # print("\n -- HTTP Headers -- ")
        # print("\tContent-Type : " + header_params['Content-Type'])
        # print("\tv-c-merchant-id : " + header_params['v-c-merchant-id'])
        # print("\tDate : " + header_params["Date"])
        # print("\tHost : " + header_params["Host"])
        # print("\tDigest : " + header_params["Digest"])
        # print("\tSignature : " + header_params["Signature"])

        # HTTP Client POST Call
        timeout = None

        try :
            r = self.pool_manager.request(method, url, body=body, preload_content=False, timeout=timeout, headers=header_params)
        except urllib3.exceptions.SSLError as e:
            msg = "{0}\n{1}".format(type(e).__name__, str(e))
            return -1

        # print("\n -- Response Message -- " )
        # print("\tResponse Code :" + str(r.status))
        # print("\tv-c-correlation-id :" + r.getheaders().get('v-c-correlation-id'))
        # print("\tResponse Data :\n" + r.data.decode('utf-8') + "\n")

        if not 200 <= r.status <= 299:
            return -1

        return r

    def process_get(self, rsrc):
        resource = rsrc
        method = 'get'

        time = self.get_time()

        token = self.get_signature(method, resource, time)

        header_params = {}
        header_params['Accept'] = 'application/hal+json;charset=utf-8'
        header_params['Content-Type'] = 'application/json;charset=utf-8'
        header_params['Accept-Encoding'] = '*'
        header_params['v-c-merchant-id'] = self.merchant_id
        header_params["Date"] = time
        header_params["Host"] = self.request_host
        header_params["User-Agent"] = "Mozilla/5.0"

        header_params["Signature"] = token

        header_params = self.sanitize_for_serialization(header_params)
        header_params = dict(self.parameters_to_tuples(header_params, None))

        url = "https://" + self.request_host + resource
        # print("\n -- RequestURL -- ")
        # print("\tURL : " + url)
        # print("\n -- HTTP Headers -- ")
        # print("\tContent-Type : " + header_params['Content-Type'])
        # print("\tv-c-merchant-id : " + header_params['v-c-merchant-id'])
        # print("\tDate : " + header_params["Date"])
        # print("\tHost : " + header_params["Host"])
        # print("\tSignature : " + header_params["Signature"])

        # HTTP Client GET Call
        timeout = None

        try :
            r = self.pool_manager.request(method, url, preload_content=False, timeout=timeout, headers=header_params)
        except urllib3.exceptions.SSLError as e:
            msg = "{0}\n{1}".format(type(e).__name__, str(e))
            return -1

        # print("\n -- Response Message -- " )
        # print("\tResponse Code :" + str(r.status))
        # print("\tv-c-correlation-id :" + r.getheaders().get('v-c-correlation-id'))
        # print("\tResponse Data :\n" + r.data.decode('utf-8') + "\n")

        if not 200 <= r.status <= 299:
            return -1

        return 0

    def process_standalone_http_signature(self):
        # HTTP POST REQUEST
        print("\n\nSample 1: POST call - CyberSource Payments API - HTTP POST Payment request")
        return self.process_post()
        # HTTP GET REQUEST
        # print("\n\nSample 2: GET call - CyberSource Reporting API - HTTP GET Reporting request")
        # status_code = self.process_get()


if __name__ == "__main__":
    standalone_http_signature_obj = StandAloneHttpSignature()
    standalone_http_signature_obj.process_standalone_http_signature()

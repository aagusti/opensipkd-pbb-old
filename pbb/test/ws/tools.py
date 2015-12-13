from datetime import datetime
import hmac
import hashlib
import base64


def json_rpc_header(userid, password):
    utc_date = datetime.utcnow()
    tStamp = int((utc_date - \
                  datetime.strptime('1970-01-01 00:00:00',
                                    '%Y-%m-%d %H:%M:%S')).\
                  total_seconds())
    value = "%s&%s" % (str(userid), tStamp)
    key = str(password) 
    signature = hmac.new(key, msg=value, digestmod=hashlib.sha256).digest() 
    encodedSignature = base64.encodestring(signature).replace('\n', '')
    return dict(userid=userid,
                signature=encodedSignature,
                key=tStamp)

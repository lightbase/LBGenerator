import requests, datetime, json
from lbgenerator.views.special import full_reg
from lbgenerator.model import BASES

class FakeRequest:

    """ Defines fake request.
        Useful for calling internal view callables.
    """
    def __init__(self, base_name, id_reg):
        self.matchdict = dict(
            base_name = base_name,
            id_reg = id_reg
        )

def to_object(js):
    if not js:
        return False
    try:
        jdec = json.JSONDecoder()
        return jdec.raw_decode(js)[0]
    except:
        return False

class Index:

    """ Handles registry index
    """
    def __init__(self, base_name):
        self.base_name = base_name

        base_obj = BASES.get_base(self.base_name)

        if base_obj.index_export == 'True':
            self.is_indexable = True
        else:
            self.is_indexable = False

        self.host = self.url_encode(
             base_obj.index_url,
             base_name,
             base_name
             )

    def url_encode(self, *args):
        return '/'.join(list(args))

    def is_created(self, msg):
        """
        Success reponse example = {
            "ok":true,
            "_index":"base1",
            "_type":"base1",
            "_id":"138",
            "_version":1
        }
        """
        if type(msg) is dict and len(msg) == 5:
            comps = 'ok' and '_index' and '_type' and '_id' and '_version'
            if comps in msg:
                return True
        return False

    def is_updated(self, msg):
        return self.is_created(msg)

    def is_deleted(self, msg):
        """
        Success reponse example = {
            "ok":true,
            "_found":true,
            "_index":"base1",
            "_type":"base1",
            "_id":"138",
            "_version":1
        }
        """
        if type(msg) is dict and len(msg) == 6:
            comps = 'ok' and '_found' and '_index' and '_type' and '_id' and '_version'
            if comps in msg:
                return True
        return False

    def create(self, data):

        if not self.is_indexable:
            return data

        url = self.url_encode(self.host, str(data.get('id_reg')))
        try:
            r = requests.post(url, data=data['json_reg'])
            r_content = bytes.decode(r.content)
        except:
            r_content = None

        if self.is_created(to_object(r_content)):
            data['dt_index_tex'] = datetime.datetime.now()
        else:
            data['dt_index_tex'] = None

        return data

    def update(self, id, data):

        if not self.is_indexable:
            return data

        url = self.url_encode(self.host, str(id))
        request = FakeRequest(self.base_name, id)
        _full_reg = full_reg(request, json_reg=data['json_reg']).text

        try:
            r = requests.put(url, data=_full_reg)
            r_content = bytes.decode(r.content)
        except:
            r_content = None

        if self.is_updated(to_object(r_content)):
            data['dt_index_tex'] = datetime.datetime.now()
        else:
            data['dt_index_tex'] = None

        return data

    def delete(self, id):

        if not self.is_indexable:
            return False

        url = self.url_encode(self.host, str(id))
        try:
            r = requests.delete(url)
            r_content = bytes.decode(r.content)
        except:
            r_content = None

        if self.is_deleted(to_object(r_content)):
            response = True
        else:
            response = False

        return response

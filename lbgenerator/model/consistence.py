
import json
from lbgenerator.model import (
      begin_session,
      doc_hyper_class
      )

def to_object(js):
    if not js:
        return False
    try:
        jdec = json.JSONDecoder()
        return jdec.raw_decode(js)[0]
    except:
        return False

def is_doc(dic, id=None):
    response = False
    if type(dic) is dict and len(dic) == 3:
        doc = 'id_doc' and 'nome_doc' and 'mimetype'
        if id: same_id = int(dic.get('id_doc')) == int(id)
        else: same_id = True
        if doc in dic and same_id:
            response = True
    return response


def normalize(base_name, session, data):

    """
    This method sincronizes database doc objecs and doc fields within json_reg.
    If provided param data is diferent from data returned:
    That means that something in REST API is inconsistent, and must be analized.
    """

    DocHyperClass = doc_hyper_class(base_name)

    json_reg = to_object(data['json_reg'])
    if not json_reg:
        raise Exception('Could not normalize data')
    id_reg = int(json_reg['id_reg'])

    docs = session.query(DocHyperClass.id_doc).filter_by(id_reg=id_reg).all()
    # docs = [(1,), (2,) ... ]

    del_fields = list()
    for field in json_reg:
        if is_doc(json_reg[field]):

            id_doc = json_reg[field]['id_doc']
            if not (id_doc,) in docs:
                del_fields.append(field)
            else:
                i = docs.index((id_doc,))
                docs.pop(i)

    # DELETE DOCUMENT-FIELDS THAT DOES NOT EXIST ON DATABASE
    for field in del_fields:
        del json_reg[field]

    data.update({'json_reg':json.dumps(json_reg, ensure_ascii=False)})

    # DELETE DATABASE-DOCUMENTS THAT ARE NOT IN JSON_REG
    for doc in docs:
        session.query(DocHyperClass).filter_by(id_doc=doc[0]).delete()

    return data

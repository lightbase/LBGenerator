
from sqlalchemy.orm.state import InstanceState
from lbgenerator.model.context import CustomContextFactory
from lbgenerator.model.index import Index
from lbgenerator.model import reg_hyper_class
from lbgenerator.model import doc_hyper_class
from lbgenerator.lib import utils
from lbgenerator.lib.consistency import Consistency
import json
import datetime

class RegContextFactory(CustomContextFactory):

    """ Registry Factory Methods.
    """

    def __init__(self, request):
        super(RegContextFactory, self).__init__(request)
        base = self.get_base()
        self.entity = reg_hyper_class(self.base_name, **base.custom_columns)
        self.doc_entity = doc_hyper_class(self.base_name)
        self.index = Index(base, self.get_full_reg)

    def create_docs(self, id):
        """ Create all documents relationated with given id
        """
        base = self.get_base()
        docs = base.__docs__[int(id)]
        for doc in docs:
            doc_member = self.doc_entity(**doc)
            self.session.add(doc_member)
        # Clear memory
        del base.__docs__[int(id)]

    def create_member(self, data):
        """ Create regitry
        """
        # Create member
        member = self.entity(**data)
        self.session.add(member)
        self.session.flush()

        if 'json_reg' in data:
            # Index member and create documents
            data = self.index.create(data)
            self.create_docs(data['id_reg'])

        for name in data:
            setattr(member, name, data[name])

        self.session.commit()
        self.session.close()
        return member

    def update_member(self, id, data):
        """ Update regitry
        """
        member = self.get_member(id)
        if member is None:
            return None

        if 'json_reg' in data:
            consistency = Consistency(self.get_base(), data['json_reg'])
            data['json_reg'] = consistency.normalize()

        for name in data:
            # Update member
            setattr(member, name, data[name])
        self.session.flush()

        # Index member and create documents
        if 'json_reg' in data:
            data = self.index.update(id, data)
            self.create_docs(id)

        for name in data:
            setattr(member, name, data[name])

        self.session.commit()
        self.session.close()
        return member

    def delete_member(self, id):
        """ Delete regitry
        """
        member = self.get_member(id)
        if member is None:
            return None

        if member.dt_reg_del:
            # Member was deleted once, but it's index was not successfull deleted.
            # This time we will force it's deletion ...
            self.session.delete(member)
        # DELETE INDEX 
        elif self.index.delete(id):
            # DELETE MEMBER
            self.session.delete(member)
        else:
            member = self.clear_del_data(id, member)

        self.delete_referenced_docs(id)
        self.session.commit()
        self.session.close()
        return member

    def clear_del_data(self, id, member):
        """ This method should be called when index deletion was not possible.
            Will set None to all columns except json_reg and dt_reg_del.
        """
        for attr in member.__dict__:
            static_attrs = isinstance(member.__dict__[attr], InstanceState)\
            or attr == 'id_reg' or attr == 'dt_reg'
            if not static_attrs:
                setattr(member, attr, None)
        setattr(member, 'dt_reg_del', datetime.datetime.now())
        setattr(member, 'json_reg', '{"id_reg":%s}' % str(id))
        return member

    def delete_referenced_docs(self, id):
        """ All docs are relationated with a registry.
            This method deletes all docs referenced by param: id
        """
        ref_docs = self.session.query(self.doc_entity).filter_by(id_reg = id)
        if ref_docs is None: return None
        ref_docs.delete()

    def get_full_reg(self, registry, close_session=True):
        """ This method will return the registry with documents texts
            within it.
        """
        id = registry['id_reg']
        doc_cols = (
           self.doc_entity.id_doc,
           self.doc_entity.texto_doc,
           self.doc_entity.grupos_acesso,
           self.doc_entity.dt_ext_texto
        )
        documents = self.session.query(*doc_cols).filter_by(id_reg = id).all()
        if close_session:
            self.session.close()
        files = { }
        if documents:
            for document in documents:
                files[document.id_doc] = dict(
                    texto_doc = document.texto_doc,
                    grupos_acesso = document.grupos_acesso,
                    dt_ext_texto = str(document.dt_ext_texto)
                )
        return self.put_doc_text(registry, files)

    def put_doc_text(self, registry, files):
        """ This method will parse a registry, find files within it,
            and then update each file (with text, if exists)
        """
        if type(registry) is dict:
            _registry = registry.copy()
        elif type(registry) is list:
            _registry = {registry.index(i): i for i in registry}
        for k, v in _registry.items():
            if type(v) is dict and utils.is_file_mask(v):
                _file = files.get(v['id_doc'])
                if _file: v.update(_file)
            elif type(v) is dict or type(v) is list:
                registry[k] = self.put_doc_text(v, files)
        return registry

    def member_to_dict(self, member, fields=None):
        if fields is None:
            fields = self.default_fields
        d = dict()
        for name in fields:
            attr = getattr(member, name)
            if name == 'json_reg' and attr is not None:
                attr = utils.to_json(attr)
            d[name] = attr
        return d

    def to_json(self, value, fields=None, wrap=True):
        obj = self.get_json_obj(value, fields, wrap)
        if getattr(self, 'single_member', None) is True and type(obj) is list:
            obj = obj[0].get('json_reg')
        return json.dumps(obj, cls=self.json_encoder, ensure_ascii=False)

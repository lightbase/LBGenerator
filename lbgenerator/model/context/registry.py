
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.util import KeyedTuple
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
        self.entity = reg_hyper_class(self.base_name, **base.relational_fields)
        self.doc_entity = doc_hyper_class(self.base_name)
        self.index = Index(base, self.get_full_reg)

    def create_docs(self, docs):
        """ Create all documents relationated with given id
        """
        for doc in docs:
            doc_member = self.doc_entity(**doc)
            self.session.add(doc_member)

    def sync_metadata(self, data):
        data['json_reg']['_metadata']['dt_index_tex'] = data.get('dt_index_tex', None)

    def create_member(self, data):
        """ Create regitry
        """
        # Create member
        member = self.entity(**data)
        self.session.add(member)

        if 'json_reg' in data:
            # Index member 
            data = self.index.create(data)
            self.sync_metadata(data)

            # Create documents
            self.create_docs(data['__docs__'])

            # Serialize registry
            data['json_reg'] = utils.registry2json(data['json_reg'])

        for name in data:
            setattr(member, name, data[name])

        self.session.commit()
        self.session.close()
        return member

    def update_member(self, member, data):
        """ Update registry
        """

        if 'json_reg' in data:

            # Normalize registry
            consistency = Consistency(self.get_base(), data['json_reg'])
            data['json_reg'] = consistency.normalize()

            # Index member 
            data = self.index.update(member.id_reg, data)
            self.sync_metadata(data)

            # Create documents
            self.create_docs(data['__docs__'])

            # Serialize registry 
            data['json_reg'] = utils.registry2json(data['json_reg'])

        for name in data:
            setattr(member, name, data[name])

        self.session.commit()
        self.session.close()
        return member

    def delete_member(self, id):
        """ Delete registry
        """
        member = self.get_member(id)
        if member is None:
            return None

        if member.dt_reg_del is not None:
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
            or attr in ['id_reg', 'dt_reg', 'dt_last_up']
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
        id = registry['_metadata']['id_reg']
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
        if not isinstance(member, KeyedTuple):
            member = self.member2KeyedTuple(member)
        dict_member = member._asdict()
        if 'json_reg' in dict_member:
            dict_member['json_reg'] = utils.json2object(dict_member['json_reg'])
        if self.default_query is True:
            dict_member = dict_member['json_reg']
        return dict_member

    def to_json(self, value, fields=None, wrap=True):
        obj = self.get_json_obj(value, fields, wrap)
        if getattr(self, 'single_member', None) is True and type(obj) is list:
            obj = obj[0]
        return json.dumps(obj, cls=self.json_encoder, ensure_ascii=False)

    def get_docs_text_by_registry_id(self, id_reg, close_session=True):
        """
        @param id_reg: id from registry 
        @param close_session: If true, will close current session, else will not.

        This method will return a dictonary in the format {id_doc: texto_doc},
        with all docs referenced by @param: id_reg
        """

        # Query documents
        documents = self.session.query(self.doc_entity.id_doc, self.doc_entity.texto_doc)\
            .filter_by(id_reg=id_reg).all() or [ ]

        if close_session is True:
            # Close session if param close_session is True
            self.session.close()

        files = { }
        for document in documents:
            # Build dictionary
            files[document.id_doc] = document.texto_doc

        return files


from lbgenerator.model.context import CustomContextFactory
from lbgenerator.model.entities import *
from lbgenerator.model import BASES
from lbgenerator.model import reg_hyper_class
from lbgenerator.model import doc_hyper_class
from lbgenerator.lib import utils

class RegContextFactory(CustomContextFactory):

    def __init__(self, request):
        super(RegContextFactory, self).__init__(request)
        custom_columns = BASES.get_base(self.base_name).custom_columns
        self.entity = reg_hyper_class(self.base_name, **custom_columns)

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

    def delete_member(self, id):
        return super(RegContextFactory, self).delete_member(id, is_reg=True)

    def delete_referenced_docs(self, id_reg):
        """ All docs are relationated with a reg.
            This method deletes all docs referenced by this id_reg
        """
        DocHyperClass = doc_hyper_class(self.base_name)
        ref_docs = self.session.query(DocHyperClass).filter_by(id_reg = id_reg)
        if ref_docs is None: return None
        ref_docs.delete()

    def get_full_reg(self, registry):

        id = registry['id_reg']
        DocHyperClass = doc_hyper_class(self.base_name)

        doc_cols = (
           DocHyperClass.id_doc,
           DocHyperClass.texto_doc,
           DocHyperClass.grupos_acesso,
           DocHyperClass.dt_ext_texto
        )

        self.files = { }
        documents = self.session.query(*doc_cols).filter_by(id_reg = id).all()
        self.session.close()
        if documents:
            for document in documents:
                self.files[document.id_doc] = dict(
                    texto_doc = document.texto_doc,
                    grupos_acesso = document.grupos_acesso,
                    dt_ext_texto = str(document.dt_ext_texto)
                )

        return self.put_doc_text(registry)

    def put_doc_text(self, registry):

        if type(registry) is dict:
            _registry = registry.copy()
        elif type(registry) is list:
            _registry = {registry.index(i): i for i in registry}

        for k, v in _registry.items():

            if type(v) is dict and utils.is_file_mask(v):
                id = v['id_doc']
                v.update(self.files[id])
            elif type(v) is dict or type(v) is list:
                registry[k] = self.put_doc_text(v)

        return registry

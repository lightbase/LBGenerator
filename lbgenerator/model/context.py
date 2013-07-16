from lbgenerator.model.entities import *
from lbgenerator.model import consistence
import json, inspect, requests, datetime
import sqlalchemy
from sqlalchemy import asc, desc
from sqlalchemy.orm.state import InstanceState
from lbgenerator.model.restexception import RestException
from pyramid_restler.model import SQLAlchemyORMContext
from lbgenerator.model.index import Index
from lbgenerator.model import (
      begin_session,
      engine,
      metadata,
      base_context,
      get_bases,
      reg_hyper_class,
      doc_hyper_class
      )

exception = RestException()

class CustomContextFactory(SQLAlchemyORMContext):

    def __init__(self, request):
        self.request = request
        self.base_name = self.request.matchdict.get('basename')
        if self.base_name:
            self.index = Index(self.base_name)

    def session_factory(self):
        return begin_session()

    def _execute(self, seq):
        """ Get next value from sequence.
        """
        seq.create(bind=engine)
        value = self.session.execute(seq)
        return value

    def get_cols(self):
        cols = tuple()
        for field in self.default_fields:
            if field != 'blob_doc':
                col = (getattr(self.entity, field),)
                cols += col
        if not 'id_doc' in self.default_fields and 'blob_doc' in self.default_fields:
            cols += (getattr(self.entity, 'id_doc'),)
        return cols

    def get_member(self, id, force=False):
        self.single_member = True
        if 'blob_doc' in self.default_fields and not force:
            q = self.session.query(*self.get_cols()).filter_by(id_doc=id)
            return q.all() or None
        q = self.session.query(self.entity)
        return q.get(id)

    def create_member(self, data):
        # CREATE MEMBER
        member = self.entity(**data)
        self.session.add(member)
        self.session.flush()

        # INDEX MEMBER
        if 'json_reg' in data:
            data = self.index.create(data)
        for name in data:
            setattr(member, name, data[name])
        self.session.commit()
        self.session.close()
        return member

    def update_member(self, id, data, index=True):
        member = self.get_member(id, force=True)
        if member is None:
            return None

        # UPDATE MEMBER
        if 'json_reg' in data and index is True:
            data = consistence.normalize(self.base_name, self.session, data)
        for name in data:
            setattr(member, name, data[name])
        self.session.flush()

        # INDEX MEMBER
        if 'json_reg' in data and index is True:
            data = self.index.update(id, data)
        for name in data:
            setattr(member, name, data[name])

        self.session.commit()
        self.session.close()
        return member

    def clear_del_data(self, id, member):
        for attr in member.__dict__:
            static_attrs = isinstance(member.__dict__[attr], InstanceState)\
            or attr == 'id_reg' or attr == 'dt_reg'
            if not static_attrs:
                setattr(member, attr, None)
        setattr(member, 'dt_reg_del', datetime.datetime.now())
        setattr(member, 'json_reg', '{"id_reg":%s}' % str(id))
        return member

    def delete_member(self, id, is_reg=False):
        member = self.get_member(id, force=True)
        if member is None:
            return None
        if is_reg:
            if self.index.delete(id):
                self.session.delete(member)
            else:
                member = self.clear_del_data(id, member)
        self.session.commit()
        self.session.close()
        return member

    def get_collection(self, select=None, distinct=False, order_by=None, limit=None,
                       offset=None, filters=None, literal=None):

        if select and select != '*':
            self.default_fields = list()
            for s in select: self.default_fields.append(s)

        cols = self.get_cols()
        q = self.session.query(*cols)

        def filter_query(q, f, expr='None'):
            field, operation, term = getattr(self.entity, f['field']), f['operation'], f['term']

            if operation == '=':
                q = q.filter(field == term)
            elif operation == 'contains':
                q = q.filter(field.contains(term))
            elif operation == 'like':
                q = q.filter(field.like(term))
            else: expr = 'self.entity.{0} {1} "{2}"'.format(f['field'], operation, term)
            return q.filter(eval(expr))

        if filters:
            if type(filters) is not list: raise Exception('filters must be list')
            for f in filters: q = filter_query(q, f)
        if literal:
            exc = RestException()
            exc.is_sqlinject(str(literal))
            q = q.filter(literal)
        if type(select) is list and len(select) == 0:
            self.default_fields = list()
        if distinct:
            q = q.distinct()
        if order_by is not None:
            for o in order_by:
                order = getattr(sqlalchemy, o)
                for i in order_by[o]: q = q.order_by(order(i))

        self.total_count = q.count()

        frame = inspect.currentframe()
        k, a, w, v = inspect.getargvalues(frame)
        args = {i: v[i] for i in k if i != 'self'}

        kwargs = False
        for i in args:
            if args[i] is None or args[i] is False: pass
            else: kwargs = True

        if not kwargs:
            self.default_offset = 0
            self.default_limit = 10
        else:
            self.default_offset = None
            self.default_limit = None

        if offset is not None:
            self.default_offset = offset
        if limit is not None:
            self.default_limit = limit

        q = q.offset(self.default_offset)
        q = q.limit(self.default_limit)

        return q.all()

    def to_json(self, value, fields=None, wrap=True):
        obj = self.get_json_obj(value, fields, wrap)
        if fields is not None and len(fields) is 1 and fields[0] == 'json_reg' and wrap is False:
            obj = obj[0].get('json_reg')
        elif getattr(self, 'single_member', None) is True and type(obj) is list:
            obj = obj[0]

        return json.dumps(obj, cls=self.json_encoder, ensure_ascii=False)

    def wrap_json_obj(self, obj):
        count = len(obj)
        if hasattr(self, 'total_count'): count = self.total_count
        # Select no fields:
        if self.default_fields is not None and len(self.default_fields) is 0: obj = list()

        limit = getattr(self, 'default_limit', 10)
        limit = 0 if limit is None else limit
        offset = getattr(self, 'default_offset', 0)
        offset = 0 if offset is None else offset

        return dict(
            results = obj,
            result_count = count,
            limit = limit,
            offset = offset
        )

class BaseContextFactory(CustomContextFactory):

    entity = LB_Base

    def create_member(self, data):

        # Create reg and doc tables
        base_name, base_xml = data['nome_base'], data['xml_base']
        custom_cols = base_context.set_base_up(base_name, base_xml)['cc']
        reg_hyper_class(base_name, **custom_cols)
        doc_hyper_class(base_name)
        metadata.create_all(bind=engine)

        member = self.entity(**data)
        self.session.add(member)
        self.session.commit()
        self.session.close()
        return member

    def delete_member(self, id):
        member = self.get_member(id, force=True)
        if member is None:
            return None

        custom_columns = base_context.get_base(member.nome_base)['cc']
        if base_context.bases.get(member.nome_base) is not None:
            del base_context.bases[member.nome_base]

        # Delete parallel tables
        doc_table = get_doc_table(member.nome_base, metadata)
        reg_table = get_reg_table(member.nome_base, metadata, **custom_columns)
        metadata.drop_all(bind=engine, tables=[reg_table])
        metadata.drop_all(bind=engine, tables=[doc_table])

        # Delete base
        self.session.delete(member)
        self.session.commit()
        self.session.close()
        return member

class FormContextFactory(CustomContextFactory):

    entity = LB_Form

class RegContextFactory(CustomContextFactory):

    def __init__(self, request):
        super(RegContextFactory, self).__init__(request)
        custom_columns = base_context.get_base(self.base_name)['cc']
        self.entity = reg_hyper_class(self.base_name, **custom_columns)

    def member_to_dict(self, member, fields=None):
        if fields is None:
            fields = self.default_fields
        d = dict()
        for name in fields:
            attr = getattr(member, name)
            if name == 'json_reg' and attr is not None:
                jdec = json.JSONDecoder()
                try: attr = jdec.raw_decode(attr)[0]
                except Exception as e: raise Exception(e)
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

class DocContextFactory(CustomContextFactory):

    def __init__(self, request):
        super(DocContextFactory, self).__init__(request)
        if not self.base_name in get_bases():
            raise Exception('Base "%s" does not exist' %(self.base_name))
        self.entity = doc_hyper_class(self.base_name)

    def member_to_dict(self, member, fields=None):
        if fields is None:
            fields = self.default_fields
        host = self.request._host__get()
        obj = dict((name, getattr(member, name)) for name in fields if name != 'blob_doc')
        if 'blob_doc' in self.default_fields:
            id_doc = getattr(member, 'id_doc')
            url_list = ['http:/', host, 'api', 'doc', self.base_name, str(id_doc), 'download']
            url = '/'.join(url_list)
            obj['blob_doc'] = url
        return obj

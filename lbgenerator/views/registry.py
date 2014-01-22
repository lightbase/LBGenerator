
from lbgenerator.views import CustomView
from lbgenerator.lib.validation.registry import validate_reg_data
from lbgenerator.lib.validation.registry import validate_put_data
from lbgenerator.lib.validation.path import validate_path_data
from lbgenerator.lib import utils
from lbgenerator.lib.log import Logger
from pyramid.response import Response
from pyramid.exceptions import HTTPNotFound
import json

class RegCustomView(CustomView):

    """ Registry Customized View Methods.
    """
    def __init__(self, context, request):
        super(RegCustomView, self).__init__(context, request)
        self.logger = Logger(__name__)

    def _get_data(self):
        """ Get all valid data from (request) POST or PUT.
        """
        return validate_reg_data(self, self.request)

    def get_member(self):
        id = self.request.matchdict['id']
        self.fields = ['json_reg']
        self.wrap = False
        member = self.context.get_member(id)
        return self.render_to_response(member)

    def get_relational_data(self, json_reg):
        """ Extract values from registry if field is relational. 
        """
        relational_fields = self.get_base().relational_fields

        unique_data = { field: None for field in relational_fields['unique_cols'] }
        relational_data = { field: None for field in relational_fields['normal_cols'] }
        relational_data.update(unique_data)

        for field in json_reg:
            if field in relational_fields['unique_cols']:
                relational_data[field] = json_reg[field]
            elif field in relational_fields['normal_cols']:
                relational_data[field] = json_reg[field]
        return relational_data

    def get_path(self):
        """ Go further into registry and get path's value.
        """
        member = self.get_db_obj()
        if member is None:
            raise HTTPNotFound()
        base = self.get_base()
        value = base.get_path(member.json_reg, self.request.matchdict['path'])
        return Response(value, content_type='application/json')

    def set_path(self):
        """ Go further into registry and set path's value.
            Obs: Only for multivalued fields.
        """
        data = validate_path_data(self.request)
        return_obj = data.get('return')
        member = self.get_db_obj()
        if member is None:
            raise HTTPNotFound()
        base = self.get_base()
        path, value = self.request.matchdict['path'], self.request.params['value']

        # Set path
        _return = base.set_path(member.json_reg, path, value)
        registry = _return['json_reg']

        id = int(self.request.matchdict['id'])
        data = dict(json_reg = registry)
        data = validate_put_data(self, data, id)

        # Update member
        member = self.context.update_member(id, data)

        # Build Response
        if data.get('return'):
            registry = utils.to_json(member.json_reg)
            _return['json_reg'] = member.json_reg
            _return['new_value'] = base.get_path(registry, _return['new_path'])
            _return['json_path'] = base.get_path(registry, path)
            return Response(_return[data['return']], content_type='application/json')
        else:
            return Response(_return['DEFAULT'])

    def put_path(self):
        """ Go further into registry and update path's value
        """
        data = validate_path_data(self.request)
        member = self.get_db_obj()
        if member is None:
            raise HTTPNotFound()
        base = self.get_base()
        path, value = self.request.matchdict['path'], self.request.params['value']

        # Update path
        _return = base.put_path(member.json_reg, path, value)
        registry = _return['json_reg']

        id = int(self.request.matchdict['id'])
        data = dict(json_reg = registry)
        data = validate_put_data(self, data, id)

        # Update member
        member = self.context.update_member(id, data)

        # Build Response
        if data.get('return'):
            registry = member.json_reg
            _return['json_reg'] = registry
            _return['new_value'] = base.get_path(utils.to_json(registry), path)
            return Response(_return[data['return']], content_type='application/json')
        else:
            return Response(_return['DEFAULT'])

    def delete_path(self):
        """ Go further into registry and delete path.
        """
        data = validate_path_data(self.request)
        member = self.get_db_obj()
        if member is None:
            raise HTTPNotFound()
        base = self.get_base()
        path = self.request.matchdict['path']

        # Delete path
        _return = base.delete_path(member.json_reg, path)
        registry = _return['json_reg']

        id = int(self.request.matchdict['id'])
        data = dict(json_reg = registry)
        data = validate_put_data(self, data, id)

        # Update member
        member = self.context.update_member(id, data)

        # Build Response
        if data.get('return'):
            _return['json_reg'] = member.json_reg
            return Response(_return[data['return']], content_type='application/json')
        else:
            return Response(_return['DEFAULT'])

    def full_reg(self):
        """ Get documents texts and put it into registry. Return registry with documents texts.
        """
        registry = utils.to_json(self.get_db_obj().json_reg)
        registry = self.context.get_full_reg(registry)
        return Response(json.dumps(registry, ensure_ascii=False), content_type='application/json')

    def update_collection(self):
        """ Udpdate database objects
        """
        collection = self.get_collection(render_to_response=False)
        success, failure = 0, 0

        for member in collection:
            id = member.id_reg
            data = validate_reg_data(self, self.request, id=id)
            self.context.session = self.context.session_factory()
            try:
                # Try to get data and update member
                self.context.update_member(id, data)
                success = success + 1

            except Exception as e:
                failure = failure + 1

            finally:
                # Close session if is yet active
                if self.context.session.is_active:
                    self.context.session.close()

        response = {
            'success': success,
            'failure' : failure
        }

        return Response(json.dumps(response), charset='utf-8', status=200, content_type='application/json')

    def delete_collection(self):
        """ Delete database objects
        """
        collection = self.get_collection(render_to_response=False)
        success, failure = 0, 0

        for member in collection:
            id = member.id_reg
            self.context.session = self.context.session_factory()
            try:
                # Try to delete member
                self.context.delete_member(id)
                success = success + 1

            except Exception as e:
                failure = failure + 1

            finally:
                # Close session if is yet active
                if self.context.session.is_active:
                    self.context.session.close()

        response = {
            'success': success,
            'failure' : failure
        }

        return Response(json.dumps(response), charset='utf-8', status=200, content_type='application/json')


from sqlalchemy.schema import Sequence
from lbgenerator.views import CustomView
from lbgenerator.lib.validation.registry import validate_reg_data

class RegCustomView(CustomView):

    """ Customized views for reg REST app.
    """
    def __init__(self, context, request):
        super(RegCustomView, self).__init__(context, request)
        self.seq = Sequence('lb_reg_%s_id_reg_seq' %(self.base_name))
        self.data = validate_reg_data(self, request)

    def set_id_up(self, json_reg, id):
        """ Puts id_reg on it's place.
        """
        json_reg['id_reg'] = id
        return json_reg

    def get_cc_data(self, json_reg):
        """ Extracts field values from json_reg if they are relational fields 
        """
        base_cc = self._base_context()
        cc = dict()
        for j in json_reg:
            if j in base_cc['unique_cols']:
                cc[j] = json_reg[j]
            elif j in base_cc['normal_cols']:
                cc[j] = json_reg[j]
        return cc

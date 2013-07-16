
import json

class Registry:

    def __init__(self, xml_reg, json_reg, multis, commons, del_files):
        self.xml_reg = xml_reg
        self.json_reg = json.loads(json_reg.encode('UTF-8'))
        self.multi_groups = multis
        self.common_groups = commons
        self.del_files = del_files
        self.xcounter = -1
        self.params = dict()
        self.new_params = dict()
        self.nameconf = { 'root': 'LB_form', 'sep': 'campo' }


        ''' mexer no del files '''

    def set_params(self):
        """ Get form-like params from a registry pre saved registry.
        """
        reg = self.json_reg['registro']
        for obj in reg:
            if not (obj == '_baseinfo' or obj[0] == '@'):
                self.parse_reg(obj, reg[obj])

    def parse_reg(self, up_obj, obj, up_fname=None, multi=None):
        """ Navigate into the lastest saved registry and build its params.
        """
        sep = self.nameconf['sep']
        root = self.nameconf['root']

        def conf_fname(fname):
            split = fname.split('.')
            split[len(split)-2] = str(self.xcounter)
            self.xcounter -= 1
            new_fname = '.'.join(split)
            return new_fname

        if multi == 'single':
            self.params[conf_fname(up_fname)] = '#grupo'
        elif multi == 'group':
            if not up_fname in self.params:
                self.params[up_fname] = '#grupo'

        if not up_fname: nlist = [root, sep, str(self.xcounter), up_obj]
        else: nlist = [up_fname, sep, str(self.xcounter), up_obj]
        self.xcounter -= 1
        fname = '.'.join(nlist)

        if type(obj) is not dict:
            self.params[fname] = obj
        elif type(obj) is dict:

            if up_obj == 'grupo' and len(obj) is 1: #grupo não multivalorado
                k, v = obj.popitem()
                if k in self.common_groups:
                    if not fname in self.params:
                        self.params[fname] = '#grupo'
                    for k2 in v:
                        self.parse_reg(k2, v[k2], up_fname=fname)

            elif obj.get('grupo'):
                t = type(obj['grupo'])
                for obj2 in obj['grupo']:
                    if up_obj in self.multi_groups['single']: #multivalued single field
                        if t is list: # repetition > 1
                            self.parse_reg(up_obj, obj2.get(up_obj), up_fname=fname, multi='single')
                        elif t is dict: # repetition = 1
                            value = obj['grupo'].get(obj2)
                            self.parse_reg(up_obj, value, up_fname=fname, multi='single')
                    elif up_obj in self.multi_groups['group']: #multivalued group
                        if t is list: # repetition > 1
                            new_fname = conf_fname(fname)
                            for k in obj2:
                                self.parse_reg(k, obj2[k], up_fname=new_fname, multi='group')
                        elif t is dict: # repetition = 1
                            self.parse_reg(obj2, obj['grupo'][obj2], up_fname=fname, multi='group')


    def set_new_params(self, form_params):
        """ Merge two dicts in one new dict
            form_params: key:value from edit-form
            self.params: rebuilded key:value from lastest saved registry
        """
        fst_lvl = dict()
        self.new_params = form_params

        def relation(s):
            split = s.split('.')
            lvl = len(split)
            name = split[lvl-1]
            return (name, lvl)

        def add_new_param(p):
            for param in self.params:
                if param.find(p) is not -1:
                    if not param in self.new_params:
                        self.new_params[param] = self.params[param]

        for param in form_params:
            # collect first-level fields/groups
            name, lvl = relation(param)
            if lvl is 4:
                fst_lvl[name] = param


        for param in self.params:
            name, lvl = relation(param)
            if lvl is 4:
                if not name in fst_lvl:
                    add_new_param(param)











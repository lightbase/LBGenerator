import sys
import traceback

from liblightbase.lbtypes.extended import FileMask
from liblightbase.lbutils.codecs import *

class LbUseful():
    """
    Essa classe contém vários utilitários para o LightBase!
    """

    def excep_useful(self):
        """
        Esse método serve para dar um retorno amigável ao usário no 
        caso de exceção!
        """
        exceptiontype, exceptionobj, exceptiontb = sys.exc_info()
        exceptiontbcomplete = traceback.format_tb(exceptiontb)
        traceexceptionstr = "Exception Details: Type '" + str(exceptiontype) +\
                            "', Inner Exception '" + str(exceptiontbcomplete[-1]) + \
                            "', Message '" + str(exceptionobj) + "'."
        return [exceptiontype, exceptiontbcomplete, traceexceptionstr]

class Accept():

    def best_match(self, *a):
        return True

class FakeRequest(object):

    accept = Accept()

    def __init__(self, params={}, matchdict={}, method='GET'):
        self.params = params
        self.matchdict = matchdict
        self.method = method

    def add_response_callback(self, *a, **kw):
        pass

def is_integer(i):
    try:
        int(i)
        return True
    except ValueError:
        return False

def split_request(request):
    # TODO: if user send a parameter on get like '%', if not url_encoded, will 
    # raise an utf-8 decode error by webob lib. Need to fix it !!!
    return dict(request.params), request.method

def filter_params(params, valid_fields):
    for param in params:
        if param not in valid_fields:
            raise Exception('Invalid param: %s' % param)
    return dict(params)

def is_sqlinject(s):
    s = s.upper()
    sqlinject = (
        "SELECT",
        "FROM"
        "DROP",
        "INSERT",
        "DELETE",
        "UNION",
        ";",
        "--",
        "/*",
        "XP_",
        "UTL_",
        "DBMS_"
    )
    for statement in sqlinject:
        if statement in s:
            raise Exception('Invalid statements in literal search.')

def is_file_mask(mask):
    try:
        FileMask(**mask)
        return True
    except:
        return False


class DocumentPatchUtils:
    def update_dict(self, doc_dict, update_doc_dict):
        """
        Updates the document's data (doc_dict) with data from update_doc_dict.
        Keys and subkeys that aren't present in updated_doc_dict are left unchanged.
        Args:
         - doc_dict: the full document to be updated
         - update_doc_dict: a dict only with the keys that will be changed
        """
        for key, value in update_doc_dict.items():
            if isinstance(value, dict) and key in doc_dict:
                self.update_dict(doc_dict[key], update_doc_dict[key])
            elif isinstance(value, list) and key in doc_dict and self.is_list_descriptor(value):
                self.update_list(doc_dict[key], update_doc_dict[key])
            elif isinstance(value, list) and key in doc_dict and self.is_list_of_dicts(value):
                for idx, item in enumerate(value):
                    self.update_dict(doc_dict[key][idx], update_doc_dict[key][idx])
            else:
                doc_dict[key] = value

    def is_list_of_dicts(self, the_list):
        first_item = the_list[0] if len(the_list) > 0 else None
        if isinstance(first_item, dict):
            return True

        return False

    def is_list_descriptor(self, the_list):
        """
        Checks if the_list constains 'update list descriptors':
        { "$set#[pos]" : "value" } -> edit value in position [pos]
        { "$add" : "value" } -> add value at the end of list
        { "$add#[pos]" : "value" } -> add value in position [pos] and push back the rest
        { "$remove": null } -> remove last value form list
        { "$remove#[pos]" : null } -> remove value in position [pos] and pull back the rest
        { "$multi#[pos-start]#[pos-end]" : [ "value-pos-start", ..., "value-pos-end" ] -> change all values 
                      from position [pos-start] to position [pos-end] (inclusive)
        """
        first_item = the_list[0] if len(the_list) > 0 else None

        if isinstance(first_item, dict):
            for key in first_item:
                if key.startswith("$"):
                    return True

        return False

    def update_list(self, doc_list, update_doc_list):
        """
        Updates doc_list using descriptors contained in update_doc_list.
        See is_list_descriptor() for a list of possible descriptors.
        """
        for descriptor in update_doc_list:
            for key, value in descriptor.items():
                args = key.split("#")
                command = args[0]
                args = args[1:]

                command_func = DocumentPatchUtils.valid_descriptors.get(command, None)
                if command_func is None:
                    # TODO: ERROR invalid command
                    pass

                command_func(self, doc_list, value, *args)

    def list_set(self, doc_list, value, *args):
        # TODO: check args size, check if it's int
        pos = int(args[0])
        if (len(doc_list) > pos):
            if isinstance(value, dict):
                self.update_dict(doc_list[pos], value)
            elif isinstance(value, list) and self.is_list_descriptor(value):
                # TODO: arrays
                self.update_list(doc_list[pos], value)
            else:
                doc_list[pos] = value
        else:
            # TODO: ERROR position doesn't exist
            pass

    def list_add(self, doc_list, value, *args):
        if len(args) > 0:
            # TODO: check if its int
            pos = int(args[0])
            doc_list.insert(pos, value)
        else:
            # append to the end of list
            doc_list.append(value)

    def list_remove(self, doc_list, value, *args):
        if len(args) > 0:
            # TODO: check if its int
            pos = int(args[0])
            del doc_list[pos]
        else:
            # remove last
            doc_list.pop()

    def list_multi(self, doc_list, value, *args):
        if len(args) > 1 and isinstance(value, list):
            pos_start = int(args[0])
            pos_end = int(args[1])
                        
            num_elements = pos_end - pos_start + 1
            if num_elements != len(value):
                # TODO ERROR
                pass

            current_pos = pos_start

            for i in range(0, num_elements):
                if (len(doc_list) > current_pos):
                    if isinstance(value[i], dict):
                        self.update_dict(doc_list[current_pos], value[i])
                    elif isinstance(value[i], list) and self.is_list_descriptor(value[i]):
                        self.update_list(doc_list[current_pos], value[i])
                    else:
                        doc_list[current_pos] = value[i]
                else:
                    # TODO: add to end or fail?
                    # adding to the end
                    doc_list.append(value[i])

                current_pos += 1
        else:
            # TODO: ERROR
            pass

    valid_descriptors = {
        "$set": list_set,
        "$add": list_add,
        "$remove": list_remove,
        "$multi": list_multi
    }

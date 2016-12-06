"""
This file contains the OperationDispatcher class and the OperationError class

Creator: Danilo Carvalho
"""

import logging

from lbgenerator.lbrad.operations import *

class OperationDispatcher(object):
    """
    This class is responsable for executing all requested operations in the
    order in which they are requested. It also checks for errors and executes
    rollback of the operations when needed.
    """
    valid_operations = {
        "db_base_create": CreateBaseOperation,
        "db_base_read": ReadBaseOperation,
        "db_base_delete": DeleteBaseOperation,
        "db_doc_create": CreateDocumentOperation,
        "db_doc_read": ReadDocumentOperation,
        "db_doc_read_full": ReadFullDocumentOperation,
        "db_doc_read_partial": PartialReadDocumentOperation,
        "db_doc_list": ListDocumentOperation,
        "db_doc_update": UpdateDocumentOperation,
        "db_doc_update_partial": PartialUpdateDocumentOperation,
        "db_doc_delete": DeleteDocumentOperation,
        "db_file_create": CreateFileOperation,
        "db_file_create_multipart": MultipartCreateFileOperation,
        "db_file_read": ReadFileOperation,
        "db_file_delete": DeleteFileOperation,
        # TODO: others
    }

    def __init__(self, request_data, request_url=None):
        """
        Params:
         - request_data (dict): must contain:
            - "operations" (list): a list of operations to be executed (see operations.py)
            - "transaction" (boolean) [optional]: defines whether this request is a
                transaction. A transaction will be executed "atomically" so if an 
                error occurs in one of its operations, all of them will be rolled 
                back (undone).
         - request_url (string) [optional]: the url used by the client in the request
        """
        # logger
        self.logger = logging.getLogger("DEBUG")
        self.logger.setLevel(logging.WARNING)
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        self.request_data = request_data
        self.request_url = request_url
        # create operation queue
        self.operation_queue = []
        # create result list
        self.result_list = []

        # ROLLBACK
        # if the request is a transaction, operations will be rolled back in case of failure
        self.transaction = True
        # create rollback operation stack = []
        self.rollback_stack = []


    def dispatch(self):
        try:
            self._parse_request()
            self._run_operations()
        except OperationError as e:
            # TODO: return error
            return { "error": str(e.args) }

        return self.result_list

    def _parse_request(self):
        self.logger.debug("Dispatcher - _parse_request")

        if "transaction" in self.request_data:
            self.transaction = self.request_data["transaction"]

        op_list = self.request_data["operations"]

        for op_params in op_list:
            self.logger.debug("Dispatcher - op_params: " + str(op_params))
            op_type = op_params["op_type"]
            self.logger.debug("Dispatcher - op_type: " + op_type)
            if op_type not in OperationDispatcher.valid_operations:
                raise OperationError("Invalid operations: " + op_type)

            op_params["request_url"] = self.request_url

            op_class = OperationDispatcher.valid_operations[op_type]
            operation = op_class(op_params, self.transaction)
            self.operation_queue.append(operation)


    def _run_operations(self):
        self.logger.debug("Dispatcher - _run_operations")

        success = True

        for op in self.operation_queue:
            self.logger.debug("Running operation: " + str(type(op)))
            result = op.run()
            self.result_list.append(result)

            if self.transaction:
                if result["success"]:
                    context = op.get_context()
                    if context is not None:
                        self.rollback_stack.append(context)
                    else:
                        # TODO: add "empty" operation to the stack
                        pass
                else:
                    # prevent other operations from running
                    success = False
                    break

        # if there was an error in one of the operations of the transaction...
        if self.transaction:
            while len(self.rollback_stack) > 0:
                context = self.rollback_stack.pop()
                if success:
                    # commit transactions
                    context.session.commit()
                else:
                    # ... rollback by executing all undo operations in the stack
                    context.session.rollback()

                    i = len(self.rollback_stack)
                    self.result_list[i]["undone"] = True

                context.session.close()

                # TODO: for each operation in the transaction that was not executed
                # add a "not executed" result to self.result_list

    # TODO: test
    def register_operation(self, key, op_class):
        """
        Registers a custom operation.
        Args:
         - key: the operation string to be used in a request. ex: "bd_create_op"
         - op_class: the operation class, it need to be a child class of LBOperation
        """
        if key in OperationDispatcher.valid_operations:
            # TODO: raise error
            return

        if not isinstance(op_class, LBOperation):
            # TODO: raise error
            return

        OperationDispatcher.valid_operations[key] = op_class


# TODO:
class OperationError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

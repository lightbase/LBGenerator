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

    valid_operations={
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
        "db_file_delete": DeleteFileOperation

        # TODO: Others! By John Doe
    }

    def __init__(self, request_data, request_url=None):
        """
        Params:
         - request_data (dict): must contain:
            - "operations" (list): a list of operations to be executed (see 
                    operations.py)
            - "transaction" (boolean) [optional]: defines whether this request 
                    is a
                transaction. A transaction will be executed "atomically" so if 
                an error occurs in one of its operations, all of them will be 
                rolled back (undone).
         - request_url (string) [optional]: the url used by the client in the 
                request
        """

        # NOTE: Logger! By Questor
        self.logger=logging.getLogger("DEBUG")
        self.logger.setLevel(logging.WARNING)
        ch=logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        formatter=logging.Formatter('%(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        self.request_data=request_data
        self.request_url=request_url

        # NOTE: Create operation queue! By John Doe
        self.operation_queue=[]

        # NOTE: Create result list! By John Doe
        self.result_list=[]

        # NOTE: ROLLBACK - If the request is a transaction, operations will be
        # rolled back in case of failure! By John Doe
        self.transaction=True

        # NOTE: Create rollback operation "stack=[]"! By John Doe
        self.rollback_stack=[]

    def dispatch(self):
        try:
            self._parse_request()
            self._run_operations()
        except OperationError as e:

            # TODO: return error! By John Doe
            return { "error": str(e.args) }

        return self.result_list

    def _parse_request(self):
        if "transaction" in self.request_data:
            self.transaction=self.request_data["transaction"]

        op_list=self.request_data["operations"]

        for op_params in op_list:
            op_type=op_params["op_type"]
            if op_type not in OperationDispatcher.valid_operations:
                raise OperationError("Invalid operations: " + op_type)

            op_params["request_url"]=self.request_url

            op_class=OperationDispatcher.valid_operations[op_type]
            operation=op_class(op_params, self.transaction)
            self.operation_queue.append(operation)

    def _run_operations(self):
        success=True
        for op in self.operation_queue:
            result=op.run()
            self.result_list.append(result)

            if self.transaction:
                if result["success"]:
                    context=op.get_context()
                    if context is not None:
                        self.rollback_stack.append(context)
                    else:
                        # TODO: Add "empty" operation to the stack! By John Doe

                        pass
                else:

                    # NOTE: Prevent other operations from running! By John Doe
                    success=False
                    break

        # NOTE: If there was an error in one of the operations of the
        # transaction! By John Doe
        if self.transaction:
            while len(self.rollback_stack) > 0:
                context=self.rollback_stack.pop()
                if success:

                    # NOTE: Commit transactions! By John Doe
                    context.session.commit()
                else:

                    # NOTE: Rollback by executing all undo operations in the
                    # stack! By John Doe
                    context.session.rollback()

                    i=len(self.rollback_stack)
                    self.result_list[i]["undone"]=True

                context.session.close()

                # TODO: for each operation in the transaction that was not
                # executed add a "not executed" result to "self.result_list"!
                # By John Doe

    # TODO: Test! By John Doe
    def register_operation(self, key, op_class):
        """
        Registers a custom operation.
        Args:
         - key: the operation string to be used in a request. ex: 
                "bd_create_op"
         - op_class: the operation class, it needs to be a subclass of 
                LBOperation
        """

        if key in OperationDispatcher.valid_operations:
            # TODO: Raise error! By John Doe

            return

        if not isinstance(op_class, LBOperation):
            # TODO: Raise error! By John Doe

            return

        OperationDispatcher.valid_operations[key]=op_class

class OperationError(RuntimeError):
    def __init__(self, msg):
        self.msg=msg

    def __str__(self):
        return self.msg

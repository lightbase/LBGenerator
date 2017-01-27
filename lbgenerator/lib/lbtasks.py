import datetime
import threading

from pyramid.testing import DummyRequest

from . import utils
from ..model.context.document import DocumentContextFactory
from ..views.document import DocumentCustomView
from ..views.error import error_view


class LBTaskManager(object):
    def __init__(self):
        self.basename = 'lb_tasks'
        self.base_url = '/%s/doc' % self.basename
        self.dt_format = '%d/%m/%Y %H:%M:%S'
        self._purge_old()

    def create(self, name, id_user, user_agent=None, user_ip=None, progress=None):
        url = self.base_url
        now = datetime.datetime.now()
        str_now = now.strftime(self.dt_format)
        task = {
            'user_data': {
                'id_user': id_user,
                'user_agent': user_agent,
                'user_ip': user_ip
            },
            'name': name,
            'status': 'In Progress',
            'started_at': str_now
        }

        if progress:
            task['progress'] = float(progress)

        params = {
            'value': task
        }
        request = DummyRequest(path=url, params=params)
        request.method = 'POST'
        request.matchdict = {"base": self.basename}
        doc_view = DocumentCustomView(DocumentContextFactory(request), request)
        response = doc_view.create_member()
        # if ValueError is not thrown, then success    
        task_id = int(response.body)

        return task_id, self.base_url + '/' + str(task_id)

    def on_update_progress(self, task_id, progress, msg=None):
        url = self.base_url + '/' + str(task_id)
        params = {
            'value': {
                'progress': float(progress)
            }
        }
        if msg:
            params['value']['status_msg'] = msg

        request = DummyRequest(path=url, params=params)
        request.method = 'PATCH'
        request.matchdict = {
            "base": self.basename,
            "id": str(task_id)
        }
        doc_view = DocumentCustomView(DocumentContextFactory(request), request)
        response = doc_view.patch_member()

        return str(response.body) == 'UPDATED'

    def on_success(self, task_id, update_progress=False, msg=None):
        url = self.base_url + '/' + str(task_id)
        now = datetime.datetime.now()
        str_now = now.strftime(self.dt_format)
        params = {
            'value': {
                'status': 'Success',
                'finished_at': str_now
            }
        }

        if update_progress:
            params['value']['progress'] = 100.0

        if msg:
            params['value']['status_msg'] = msg

        request = DummyRequest(path=url, params=params)
        request.method = 'PATCH'
        request.matchdict = {
            "base": self.basename,
            "id": str(task_id)
        }
        doc_view = DocumentCustomView(DocumentContextFactory(request), request)
        response = doc_view.patch_member()

        self._schedule_deletion(task_id)

        return str(response.body) == 'UPDATED'

    def on_error(self, task_id, exception):
        error_msgs = [str(arg) for arg in exception.args]

        url = self.base_url + '/' + str(task_id)
        now = datetime.datetime.now()
        str_now = now.strftime(self.dt_format)
        params = {
            'value': {
                'status': 'Error',
                'finished_at': str_now,
                'error_msgs': error_msgs
            }
        }

        request = DummyRequest(path=url, params=params)
        request.method = 'PATCH'
        request.matchdict = {
            "base": self.basename,
            "id": str(task_id)
        }
        doc_view = DocumentCustomView(DocumentContextFactory(request), request)
        response = doc_view.patch_member()

        print('LBTaskManager.on_error() ended: ' + str(response.body))

        self._schedule_deletion(task_id)

        return str(response.body) == 'UPDATED'

    def _purge_old(self):
        """ Delete any task on DB that has been completed for more than 3 days
        """
        query_param = '{"literal":"(now()-finished_at) > \'P0Y0M3DT0H0M0S\'"}'
        url = self.base_url + '?$$=' + query_param
        params = {
            '$$': query_param
        }

        request = DummyRequest(path=url, params=params)
        request.method = 'DELETE'
        from webob.acceptparse import Accept
        request.accept = Accept("application/json")
        request.matchdict = {
            'base': self.basename
        }
        doc_view = DocumentCustomView(DocumentContextFactory(request), request)
        response = doc_view.delete_collection()

    def _schedule_deletion(self, task_id):
        """ Schedule a task to be deleted from DB in 3 days
        """
        print('LBTaskManager._schedule_deletion() started')

        # delete 3 days after completed
        timer_thread = threading.Timer(
            3*24*60*60,
            self._delete,
            args=(task_id,)
        )
        timer_thread.start()

    def _delete(self, task_id):
        """ Delete a task from DB
        """
        url = self.base_url + '/' + str(task_id)
        request = DummyRequest(path=url)
        request.method = 'DELETE'
        request.matchdict = {
            "base": self.basename,
            "id": str(task_id)
        }
        doc_view = DocumentCustomView(DocumentContextFactory(request), request)
        response = doc_view.delete_member()

        return str(response.body) == 'DELETED'

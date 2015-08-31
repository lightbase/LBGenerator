
import os
import cgi
import uuid
import codecs
import tarfile
import itertools
import multiprocessing
from ..lib.utils import FakeRequest
from pyramid.response import Response
from sqlalchemy.schema import Sequence
from .document import DocumentCustomView
from multiprocessing import Process, Manager
from ..model.context.document import DocumentContextFactory
from ..config import create_new_engine, create_scoped_session

BOM = codecs.BOM_UTF8.decode('utf8')
ENGINE = create_new_engine()

def _import(request):

    num_workers = int(request.params.get('workers', 15))
    file_ = request.params.get('file')
    msg = 'Please ensure file param is a File object!'
    assert isinstance(file_, cgi.FieldStorage), msg

    identifier = str(uuid.uuid4())
    gzpath = '/tmp/' + identifier + '.tar.gz'
    gzpath = os.path.abspath(gzpath)

    try:
        with open(gzpath, 'wb') as f:
            f.write(file_.file.read())
    except Exception as e:
        raise e.__class__('Error while uploading file! %s' % e)

    if not tarfile.is_tarfile(gzpath):
        os.remove(gzpath)
        return Response('Not a tar.gz file ..')

    with tarfile.open(gzpath) as gzfile:
        members = gzfile.getmembers()
        gzfile.extractall('/var/neolight')

    os.remove(gzpath)

    filepath = os.path.abspath('/var/neolight/' + members[0].name)

    request = FakeRequest(
        matchdict=request.matchdict,
        method=request.method
    )

    globals()['request'] = request

    manager = Manager()
    results = manager.list()
    work = manager.Queue(num_workers)

    # start for workers    
    pool = []
    for i in range(num_workers):
        p = Process(target=write_doc, args=(work, results))
        p.start()
        pool.append(p)

    # produce data
    with codecs.open(filepath, encoding='utf-8') as f:
        iters = itertools.chain(f, (None,) * num_workers)
        for num_and_line in enumerate(iters):
            work.put(num_and_line)

    os.remove(filepath)

    # TO DO: Specify a definition for the variables: success and failure.
    return Response('{"success": %d, "failure" : %d}' % (success, failure),
        content_type='application/json')

def _export(request):
    return Response('ççççççççççç')


def write_doc(in_queue, out_list):
    global request

    while True:
        item = in_queue.get()
        line_no, line = item

        # exit signal 
        if line == None:
            return

        line = line.lstrip(BOM)
        request.params['value'] = line

        sess = create_scoped_session(ENGINE)

        DocumentContextFactory.overwrite_session = True
        DocumentContextFactory.__session__ = sess

        base_name = request.matchdict['base']

        def _next_id():
            """ Get next value from sequence """
            seq = Sequence('lb_doc_%s_id_doc_seq' %(base_name))
            seq.create(bind=ENGINE)
            _next = sess.execute(seq)
            return _next

        context = DocumentContextFactory(request, _next_id)
        view = DocumentCustomView(context, request)

        #if not context.session.is_active:
        context.session.begin()

        #try:
        view.create_member()
        #success = success + 1
        #except:
        #failure = failure + 1

        #if context.session.is_active:
        #    context.session.close()




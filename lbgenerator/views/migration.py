import os
import cgi
import uuid
import codecs
import tarfile
import itertools
import multiprocessing
from multiprocessing import Process, Manager

from pyramid.response import Response
from sqlalchemy.schema import Sequence

from ..lib.utils import FakeRequest
from .document import DocumentCustomView
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

        # NOTE: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if request.context.session.is_active:
                request.context.session.close()
        except:
            pass

        raise e.__class__('Error while uploading file! %s' % e)

    if not tarfile.is_tarfile(gzpath):
        os.remove(gzpath)

        # NOTE: Tentar fechar a conexão de qualquer forma!
        # -> Na criação da conexão "coautocommit=True"!
        # By Questor
        try:
            if request.context.session.is_active:
                request.context.session.close()
        except:
            pass

        return Response('Not a tar.gz file ..')

    with tarfile.open(gzpath) as gzfile:
        members = gzfile.getmembers()
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(gzfile, "/tmp/neolight")

    os.remove(gzpath)

    filepath = os.path.abspath('/tmp/neolight/' + members[0].name)

    request = FakeRequest(
        matchdict=request.matchdict,
        method=request.method
    )

    globals()['request'] = request

    manager = Manager()
    results = manager.list()
    work = manager.Queue(num_workers)

    # NOTE: Start for workers! By John Doe
    pool = []
    for i in range(num_workers):
        p = Process(target=write_doc, args=(work, results))
        p.start()
        pool.append(p)

    # NOTE: Produce data! By John Doe
    success = 0
    failure = 0
    with codecs.open(filepath, encoding='utf-8') as f:
        iters = itertools.chain(f, (None,) * num_workers)
        for num_and_line in enumerate(iters):
            try:
                test = work.put(num_and_line)
                if num_and_line[1] is not None:
                    success = success +1
            except:
                failure = failure + 1

    os.remove(filepath)

    # NOTE: Tentar fechar a conexão de qualquer forma!
    # -> Na criação da conexão "coautocommit=True"!
    # By Questor
    try:
        if request.context.session.is_active:
            request.context.session.close()
    except:
        pass

    # TODO: Specify a definition for the variables: success and failure!
    # By John Doe
    return Response('{"success": %d, "failure" : %d}' % (success, failure),
        content_type='application/json')

def _export(request):

    # NOTE: Tentar fechar a conexão de qualquer forma!
    # -> Na criação da conexão "coautocommit=True"!
    # By Questor
    try:
        if request.context.session.is_active:
            request.context.session.close()
    except:
        pass

    # TODO: Tá tosco, deveria levantar um exceção! By Questor
    return Response('NOT IMPLEMENTED!')

def write_doc(in_queue, out_list):
    global request

    while True:
        item = in_queue.get()
        line_no, line = item

        # NOTE: Exit signal! By John Doe
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

        # TODO: Para o caso de necessitar! By Questor
        # context.session.begin()

        view.create_member()

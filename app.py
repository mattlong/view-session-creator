import gevent.monkey
gevent.monkey.patch_all()

import sys
import traceback
import gevent
import gevent.pool
import gevent.queue
import redis
from gevent import sleep

from client import BoxViewClient


API_TOKEN = 'TODO'
BASE_URL = None  # 'http://local.boxviewapi.com/1'
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 7,
}

def log(thing):
    sys.stdout.write(str(thing))
    sys.stdout.write('\n')
    sys.stdout.flush()


def error(thing):
    sys.stderr.write(str(thing))
    sys.stderr.write('\n')
    sys.stderr.flush()


def reconvert(client, doc_id):
    error('mocking reconversion...')
    sleep(0.2)
    return 'foo', 'bar'

    try:
        session = client.create_session(doc_id).json()
    except Exception:
        error('doc_id={0}\n{1}'.format(doc_id, traceback.format_exc()))
        return 'fail-create-session', None

    while True:
        try:
            doc = client.get_document(doc_id).json()
        except Exception:
            error.write('{0}\n{1}'.format(doc_id, traceback.format_exc()))
            return 'fail-get-document', None

        if doc['status'] == 'done':
            return doc['status'], session['id']

        elif doc['status'] == 'error':
            return doc['status'], session['id']

        elif doc['status'] in ['queued', 'processing']:
            pass

        else:  # unexpected status
            error('unexpected status "%s" for doc_id %s' % (doc['status'], doc_id))
            return doc['status'], None

        sleep(0.5)


def get_status(r, doc_id):
    return r.get('status-%s' % doc_id)


def set_status(r, doc_id, status):
    return r.set('status-%s' % doc_id, status)


def worker(name, fp):
    client = BoxViewClient(api_token=API_TOKEN, url=BASE_URL)
    rconn = redis.StrictRedis(**REDIS_CONFIG)

    while True:
        doc_id = fp.readline().strip()
        if not doc_id:
            error('%s hit end of input file, so exiting' % name)
            break

        status = get_status(rconn, doc_id)
        if status in ['done', 'error']:
            error('%s skipping doc_id %s since it already has a status of %s' % (name, doc_id, status))
            continue

        status, session_id = reconvert(client, doc_id)
        log('worker={0},doc_id={1},status={2},session_id={3}'.format(name, doc_id, status, session_id))
        set_status(rconn, doc_id, status)
        sleep(0)


if __name__ == '__main__':
    pool_size = 3
    doc_id_list_path = sys.argv[1]

    error('creating pool with %d workers...' % pool_size)
    pool = gevent.pool.Pool(pool_size)

    fp = open(doc_id_list_path)
    for n in range(pool_size):
        pool.spawn(worker, 'worker-%d' % n, fp) 
    pool.join()

from __future__ import absolute_import
# Note: Following stuff must be considered in a GangaRepository:
#
# * lazy loading
# * locking

from .GangaRepository import GangaRepository, RepositoryError
import os
import os.path
import time

import sqlite3

try:
    import cPickle as pickle
except:
    import pickle

import Ganga.Utility.logging
logger = Ganga.Utility.logging.getLogger()

import threading
from operator import itemgetter
from Ganga.Core.GangaThread.GangaThread import GangaThread
from Ganga.GPIDev.Lib.Tasks.CoreTransform import CoreTransform
from Ganga.GPIDev.Lib.Tasks.CoreTransform import CoreUnit
from Ganga.Lib.Splitters.GenericSplitter import GenericSplitter
from GangaLZ.Lib.Tasks.LZRequest import LZRequest
from GangaLZ.Lib.Applications.LZApp import LZApp
from GangaLZ.Lib.Backends.LZDirac import LZDirac
from GangaLZ.Lib.PostProcessors.DBUpdatePostProcessor import DBUpdatePostProcessor
from GangaDirac.Lib.Backends.Dirac import Dirac
from Ganga.Core.GangaRepository import getRegistrySlice
class GangaRepositoryTransientSQLite(GangaRepository):

    """GangaRepository SQLite"""

    def update_fromDB(self):
        lztask_jobs = {}
        for j in getRegistrySlice('jobs'):
            if isinstance(j.application, LZApp):
                taskid, _, unitid = j.application.requestid.split('.')
                lztask_jobs.setdefault(int(taskid),[]).append((int(unitid), j.id))
        print "LZTASK_JOBS:", lztask_jobs


        
        while not threading.current_thread().should_stop():
            with sqlite3.connect("/home/hep/arichard/git/ganga/new3rdgen/requests.db") as con:
                con.row_factory = sqlite3.Row
                for request in con.execute("SELECT * FROM requests"):
                    if request['app'] != "LUXSim":
                        continue
                    rowid = request['id']
                    if rowid in self.objects:
                        continue
                    
                    #########################################
#                    for j in lztaskjobs.get(rowid, []):
                    print "ROWID = ", rowid
                    if rowid in lztask_jobs:
                        # re-link jobs
                        t=LZRequest()
                        t.id = rowid
                        t.status = 'running'
                        tr = CoreTransform()
                        tr.status = 'running'
                        print "sorted = ", sorted(lztask_jobs[rowid], key=itemgetter(0))
                        for _, jobid in sorted(lztask_jobs[rowid], key=itemgetter(0)):
                            c =CoreUnit()
                            c.active_job_ids = [jobid]
                            c.status = 'running'
                            c.active = True
                            tr.units.append(c)
                        t.appendTransform(tr)
                        t.float = 100
                        self.objects[rowid] = t
                        continue
                    #########################################
                    logger.info("Adding new LZ task from request, id: %s", rowid)
                    t = LZRequest()
                    t.id = rowid
                    t.request = request
                    tr = CoreTransform()
                    tr.backend = LZDirac()
                    tr.application = LZApp()
                    tr.application.luxsim_version=request['app_version']
                    tr.application.reduction_version = request['reduction_version']
                    tr.application.tag = request['tag']
                    macros, njobs, nevents, seed = zip(*(i.split() for i in request['selected_macros'].splitlines()))
                    tr.unit_splitter = GenericSplitter()
                    tr.unit_splitter.multi_attrs={'application.macro': macros,
                                                  'application.njobs': [int(i) for i in njobs],
                                                  'application.nevents': [int(i) for i in nevents],
                                                  'application.seed': [int(i) for i in seed],
                                                  'application.requestid': ["%s.0.%s" %(rowid, i) for i in xrange(len(seed))]}
                    t.appendTransform(tr)
                    t.float = 100
                    self.objects[rowid] = t
#                    self.current_state[rowid] = request['status']
#                    if request['status'] == 'Approved':
#                        t.run()
            time.sleep(10)
    def startup(self):
        """ Starts an repository and reads in a directory structure."""
        self.current_state={}
        self.thread = GangaThread('LZTasks', target=self.update_fromDB)
        self.thread.start()
        '''with sqlite3.connect("/home/hep/arichard/git/ganga/new3rdgen/requests.db") as con:
            con.row_factory = sqlite3.Row
            for request in con.execute("SELECT * FROM requests"):
                if request['app'] != "LUXSim":
                    continue
                rowid = request['id']
                t = LZRequest()
                t.id = rowid
                t.request = request
                tr = CoreTransform()
                tr.backend = Dirac()
                tr.application = LZApp()
                tr.application.luxsim_version=request['app_version']
                tr.application.reduction_version = request['reduction_version']
                tr.application.tag = request['tag']
                macros, njobs, nevents, seed = zip(*(i.split() for i in request['selected_macros'].splitlines()))
                tr.unit_splitter = GenericSplitter()
                tr.unit_splitter.multi_attrs={'application.macro': macros,
                                              'application.njobs': [int(i) for i in njobs],
                                              'application.nevents': [int(i) for i in nevents],
                                              'application.seed': [int(i) for i in seed]}
                t.appendTransform(tr)
                t.float = 100
                self.objects[rowid] = t
                self.current_state[rowid] = request['status']
'''                
    def isObjectLoaded(self, id):
        return True
    def shutdown(self):
        """Shutdown the repository. Flushing is done by the Registry
        Raise RepositoryError"""
        pass
        
    def update_index(self, id=None, verbose=False):
        """ Update the list of available objects
        Raise RepositoryError"""
        # First locate and load the index files
        pass

    def add(self, objs, force_ids=None):
        """ Add the given objects to the repository, forcing the IDs if told to.
        Raise RepositoryError"""
        raise RepositoryError("Cant add")

    def flush(self, ids):
        pass
#        for id in ids:
#            if self.objects[id].status != self.current_state[id]:
#                print "FLUSHING ", id, self.objects[id].status, self.current_state[id]

    def load(self, ids):
        from Ganga.GPIDev.Lib.Job.Job import Job
        with sqlite3.connect("home/hep/arichard/git/ganga/new3rdgen/requests.db") as con:
            con.row_factory = sqlite3.Row
            for request in con.execute("SELECT * FROM requests"):
                print "loading %s" % request['id']

    def delete(self, ids):
        raise RepositoryError("DELETING")

    def lock(self, ids):
        return ids

    def unlock(self, ids):
        return ids

    def get_lock_session(self, id):
        """get_lock_session(id)
        Tries to determine the session that holds the lock on id for information purposes, and return an informative string.
        Returns None on failure
        """
        return ""

    def get_other_sessions(self):
        """get_session_list()
        Tries to determine the other sessions that are active and returns an informative string for each of them.
        """
        return []

    def reap_locks(self):
        """reap_locks() --> True/False
        Remotely clear all foreign locks from the session.
        WARNING: This is not nice.
        Returns True on success, False on error."""
        return False

    def clean(self):
        """clean() --> True/False
        Clear EVERYTHING in this repository, counter, all jobs, etc.
        WARNING: This is not nice."""
        self.shutdown()
        self.startup()

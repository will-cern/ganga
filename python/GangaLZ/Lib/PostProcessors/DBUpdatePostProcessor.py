import logging
from Ganga.GPIDev.Adapters.IPostProcessor import IPostProcessor
from Ganga.GPIDev.Schema import Schema, Version, SimpleItem
logger = logging.getLogger(__name__)

class DBUpdatePostProcessor(IPostProcessor):
    _schema = Schema(Version(1, 0), {
        'dbfile': SimpleItem(None, typelist=[str, None]),
        'requestid': SimpleItem(None, typelist=[int, None])
    })
    _category = 'postprocessor'
    _name = "DBUpdatePostProcessor"

    def execute(self, job, newstatus, **options):
        if self.dbfile is None or self.requestid is None:
            raise TypeError("reqiestid and dbfile must be set")
        try:
            with sqlite3.connect(self._dbfile) as con:
                con.execute('UPDATE requests SET status=? WHERE id=?', (newstatus, self._requestid))
        except Exception as e:
            logger.exception("Exception while trying to update the database")
            return False
    
        logger.info("DB updated to %s", newstatus)
        return True

import os
import sys
import time

from enum import Enum

class Logger(object):
    class LogLevel(Enum):
        INFO = 0
        DEBUG = 1
        WARN = 2
        ERROR = 3
        FATAL = 4

    level_to_string = {
        LogLevel.INFO: 'INFO',
        LogLevel.DEBUG: 'DEBUG',
        LogLevel.WARN: 'WARN',
        LogLevel.ERROR: 'ERROR',
        LogLevel.FATAL: 'FATAL',
    }

    def __init__(self, file=sys.stdout):
        self._file = file

    def info(self, message, *args, **kwargs):
        self._log(Logger.LogLevel.INFO, (message % args))

    def warning(self, message, *args, **kwargs):
        self._log(Logger.LogLevel.INFO, (message % args))

    def debug(self, message, *args, **kwargs):
        self._log(Logger.LogLevel.INFO, (message % args))

    def error(self, message, *args, **kwargs):
        self._log(Logger.LogLevel.INFO, (message % args))

    def _log(self, level, message):
        timestamp = time.strftime('[%Y-%m-%d %H:%M:%S]') 
        # TO-DO: get caller info
        msg = '%s %s %s\n' % (timestamp, self.level_to_string[level], message)
        self._file.write(msg)


    



if __name__ == '__main__':
    print(Logger.level_to_string[Logger.LogLevel.INFO])


    def debug(self, message, *args, **kwargs):
        self._log(Logger.LogLevel.INFO, (message % args))
    def _log(self, level, message):
        timestamp = time.strftime('[%Y-%m-%d %H:%M:%S]') 
        # TO-DO: get caller info
        msg = '%s %s %s\n' % (timestamp, self.level_to_string[level], message)
        self._file.write(msg)


    



if __name__ == '__main__':
    print(Logger.level_to_string[Logger.LogLevel.INFO])



    def _log(self, level, message):
        timestamp = time.strftime('[%Y-%m-%d %H:%M:%S]') 
        # TO-DO: get caller info
        msg = '%s %s %s\n' % (timestamp, self.level_to_string[level], message)
        self._file.write(msg)


    



if __name__ == '__main__':
    print(Logger.level_to_string[Logger.LogLevel.INFO])


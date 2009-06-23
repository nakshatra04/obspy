#!/usr/bin/env python
# -*- coding: utf-8 -*-

from calendar import timegm
import datetime
import traceback


class Stats(dict):
    """
    A stats class which behaves like a dictionary.
    
    You may the following syntax to change or access data in this class:
      >>> stats = Stats()
      >>> stats.network = 'BW'
      >>> stats['station'] = 'ROTZ'
      >>> stats.get('network')
      'BW'
      >>> stats['network']
      'BW'
      >>> stats.station
      'ROTZ'
      >>> x = stats.keys()
      >>> x.sort()
      >>> x[0:3]
      ['channel', 'dataquality', 'endtime']

    @type station: String
    @ivar station: Station name
    @type sampling_rate: Float
    @ivar sampling_rate: Sampling rate
    @type npts: Int
    @ivar npts: Number of data points
    @type network: String
    @ivar network: Stations network code
    @type location: String
    @ivar location: Stations location code
    @type channel: String
    @ivar channel: Channel
    @type dataquality: String
    @ivar dataquality: Data quality
    @type starttime: obspy.DateTime Object
    @ivar starttime: Starttime of seismogram
    @type endtime: obspy.DateTime Object
    @ivar endtime: Endtime of seismogram
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self
        # fill some dummy values
        self.station = "dummy"
        self.sampling_rate = 1.0
        self.npts = -1
        self.network = "--"
        self.location = ""
        self.channel = "BHZ"
        self.dataquality = ""
        self.starttime = DateTime.utcfromtimestamp(0.0)
        self.endtime = DateTime.utcfromtimestamp(86400.0)


class DateTime(datetime.datetime):
    """
    A class handling conversion from utc datetime to utc timestamps. 
    
    This class inherits from datetime.datetime and refines the UTC timezone 
    support.
    
    You may use the following syntax to change or access data in this class:
        >>> DateTime(0.0)
        DateTime(1970, 1, 1, 0, 0)
        >>> DateTime(1970, 1, 1)
        DateTime(1970, 1, 1, 0, 0)
        >>> t = DateTime(1240561632.005)
        >>> t
        DateTime(2009, 4, 24, 8, 27, 12, 5000)
        >>> t.year
        2009
        >>> t.year, t.hour, t.month, t.hour, t.minute, t.second, t.microsecond
        (2009, 8, 4, 8, 27, 12, 5000)
        >>> t.timestamp() + 100
        1240561732.0050001
        >>> t2 = DateTime(t.timestamp()+60)
        >>> t2
        DateTime(2009, 4, 24, 8, 28, 12, 5000)
        >>> DateTime(datetime.datetime(2009, 5, 24, 8, 28, 12, 5001))
        DateTime(2009, 5, 24, 8, 28, 12, 5001)

    """
    def __new__(cls, *args, **kwargs):
        if len(args) == 1:
            arg = args[0]
            if type(arg) in [int, long, float]:
                dt = datetime.datetime.utcfromtimestamp(arg)
                return datetime.datetime.__new__(cls, dt.year, dt.month,
                                                 dt.day, dt.hour,
                                                 dt.minute, dt.second,
                                                 dt.microsecond)
            elif isinstance(arg, datetime.datetime):
                dt = arg
                return datetime.datetime.__new__(cls, dt.year, dt.month,
                                                 dt.day, dt.hour,
                                                 dt.minute, dt.second,
                                                 dt.microsecond)
        return datetime.datetime.__new__(cls, *args, **kwargs)

    def timestamp(self):
        """
        Return UTC timestamp in floating point seconds
        
        @rtype: float
        @return: Timestamp in seconds
        """
        #XXX: datetime.strftime("%s") is not working in windows
        #os.environ['TZ'] = 'UTC'
        #return float(self.strftime("%s")) + self.microsecond/1.0e6
        return float(timegm(self.timetuple())) + self.microsecond / 1.0e6


def getFormatsAndMethods(verbose=False):
    """
    Collects all obspy parser classes.

    @type verbose: Bool
    @param verbose: Print error messages/ exceptions while parsing.
    """
    temp = []
    failure = []
    # There is one try-except block for each supported file format.
    try:
        from obspy.mseed.core import isMSEED, readMSEED, writeMSEED
        # The first item is the name of the format, the second the checking function.
        temp.append(['MSEED', isMSEED, readMSEED, writeMSEED])
    except:
        failure.append(traceback.format_exc())
    try:
        from obspy.gse2.core import isGSE2, readGSE2, writeGSE2
        # The first item is the name of the format, the second the checking function.
        temp.append(['GSE2', isGSE2, readGSE2, writeGSE2])
    except:
        failure.append(traceback.format_exc())
    try:
        from obspy.wav.core import isWAV, readWAV, writeWAV
        # The first item is the name of the format, the second the checking function.
        temp.append(['WAV', isWAV, readWAV, writeWAV])
    except:
        failure.append(traceback.format_exc())
    if verbose:
        for _i in xrange(len(failure)):
            print failure[_i]
    return temp


def scoreatpercentile(a, per, limit=(), sort=True):
    """
    Calculates the score at the given 'per' percentile of the sequence a.
    
    For example, the score at per=50 is the median.
    
    If the desired quantile lies between two data points, we interpolate
    between them.
    
    If the parameter 'limit' is provided, it should be a tuple (lower,
    upper) of two values.  Values of 'a' outside this (closed) interval
    will be ignored.
    
        >>> a = [1, 2, 3, 4]
        >>> scoreatpercentile(a, 25)
        1.75
        >>> scoreatpercentile(a, 50)
        2.5
        >>> scoreatpercentile(a, 75)
        3.25
        >>> a = [6, 47, 49, 15, 42, 41, 7, 39, 43, 40, 36]
        >>> scoreatpercentile(a, 25)
        25.5
        >>> scoreatpercentile(a, 50)
        40
        >>> scoreatpercentile(a, 75)
        42.5
    
    This method is taken from scipy.stats.scoreatpercentile
    Copyright (c) Gary Strangman
    """
    if sort:
        values = sorted(a)
        if limit:
            values = values[(limit[0] < a) & (a < limit[1])]
    else:
        values = a

    def _interpolate(a, b, fraction):
        return a + (b - a) * fraction;

    idx = per / 100. * (len(values) - 1)
    if (idx % 1 == 0):
        return values[int(idx)]
    else:
        return _interpolate(values[int(idx)], values[int(idx) + 1], idx % 1)


if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)

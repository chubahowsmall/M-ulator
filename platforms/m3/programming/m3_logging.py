#!/usr/bin/env python2
# vim: sts=4 ts=4 sw=4 noet:

import os
import logging
logging.captureWarnings(True)

TRACE_LEVEL=25
logging.addLevelName(TRACE_LEVEL, 'TRACE')

class DefaultFormatter(logging.Formatter):
	def __init__(self, fmt="%(levelname)s\t%(message)s"):
		super(DefaultFormatter, self).__init__(fmt)

class NoTraceFilter(logging.Filter):
	def filter(self, record):
		return not record.levelno == TRACE_LEVEL

def is_lambda(fn):
	# This is a little fragile, but really this whole introspection idea is, so
	# let's roll with it for now
	return isinstance(fn, type(lambda: None)) and fn.__name__ == '<lambda>'

import inspect
def trace(fn):
	"""Decorator that logger.trace()'s function calls and their arguments"""
	def inner(*args, **kwargs):
		if is_lambda(fn):
			source = inspect.getsource(fn).strip()
			source = source.replace('\\\n', '')
			source = source.replace('\n', '')
			source = source.replace('\t', ' ')
			while source.find('  ') != -1:
				source = source.replace('  ', ' ')
			if source.find('command') != -1:
				source = source[source.find('command'):]
			logger.trace('{} *args={} **kwargs={}'.format(source, args, kwargs))
		else:
			logger.trace('{} *args={} **kwargs={}'.format(fn.__name__, args, kwargs))
		#for frame in inspect.stack():
		#	logger.trace(frame)
		#	logger.trace(inspect.getframeinfo(frame[0]))
		#	logger.trace(inspect.getargvalues(frame[0]))
		#	logger.trace(' ')
		#logger.trace(inspect.getargvalues(inspect.trace()[0][0]))
		return fn(*args, **kwargs)
	return inner

no_trace_filter = NoTraceFilter()

def get_logger(name):
	l = logging.getLogger(name)
	l.level = logging.DEBUG
	try:
		l.addHandler(get_logger.handler)
	except AttributeError:
		h = logging.StreamHandler()
		h.level = log_level_from_environment()
		h.addFilter(NoTraceFilter())
		get_logger.handler = h
		l.addHandler(get_logger.handler)
	try:
		get_logger.handler.setFormatter(get_logger.formatter)
	except AttributeError:
		f = DefaultFormatter()
		get_logger.formatter = f
		get_logger.handler.setFormatter(get_logger.formatter)

	l.trace = lambda msg, l=l: l.log(TRACE_LEVEL, msg)

	return l

def log_level_from_environment():
	try:
		os.environ['ICE_DEBUG']
		return logging.DEBUG
	except KeyError:
		return logging.INFO

logger = get_logger(__name__)

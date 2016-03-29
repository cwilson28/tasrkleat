import os

from argsparser import parse_args


def gen_config():
    project_id = os.path.environ['PROJECT_ID']
    args = parse_args()

    config = {
        'input_bam': args.input_bam,
        'num_cpus': args.num_threads
    }

    config['output_dir'] = os.path.join(
        os.path.dirname(config['input_bam']), '{0}-results'.format(project_id))

    output_log_file = args.output_log
    if not output_log_file:
        output_log_file = os.path.join(
            config['output_dir'], '{0}.log'.format(project_id))

    try:
        os.makedirs(config['output_dir'])
    except OSError:
        pass

    config['logging'] = configure_logging_dict(output_log_file)
    return config


def configure_logging_dict(output_log_file):
    return {
        'version': 1,
        'disable_existing_loggers': True,

        'loggers': {
            '__main__': {
                'handlers': ['screen', 'file'],
                'level': 'DEBUG',
                'propagate': True,
                },
            'utils': {
                'handlers': ['screen', 'file'],
                'level': 'DEBUG',
                'propagate': True,
                },
            },

        'formatters': {
            'verbose': {
                'format': '%(levelname)s|%(asctime)s|%(name)s|%(module)s|%(process)d|%(processName)s|%(relativeCreated)d|%(thread)d|%(threadName)s|%(msecs)d ms|%(pathname)s+%(lineno)d|%(funcName)s:%(message)s'
                },
            'standard': {
                'format': '%(levelname)s|%(asctime)s|%(name)s:%(message)s'
                },
            'colorful': {
                # https://github.com/borntyping/python-colorlog#with-dictconfig
                '()': 'colorlog.ColoredFormatter',
                'format': '%(log_color)s%(levelname)s%(reset)s|%(log_color)s[%(asctime)s]%(reset)s|%(log_color)s%(name)s%(reset)s:%(message)s'
                }
            },

        'handlers': {
            'screen':{
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'colorful'
                },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': output_log_file,
                'formatter': 'standard'
                },
            },
        }

CONFIG = gen_config()

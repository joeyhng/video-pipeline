import os.path as osp
import multiprocessing
import functools

def _run_single(x, modules=None, log_dir=None):
    '''Move out from the class so that we can use multiprocessing'''
    ox = x[1] if len(x) == 2 else x
    log_path = osp.join(log_dir, ox + '.done')
    if osp.exists(log_path):
        return None

    try:
        for module in modules:
            x = module.run(x)
            if x is None:
                open(osp.join(log_dir, ox + '.failed'), 'w').close()
                break

        for module in modules:
            module.close()

        open(log_path, 'w').close()
    except IOError:
        pass

    return x


class VideoPipeline:
    '''Pipeline for video processing.

    Each module should be a PipelineModule
    '''

    def __init__(self, n_job=1, log_dir='/tmp/'):
        self.modules = []
        self.n_job = n_job
        self.log_dir = log_dir


    def add(self, module):
        self.modules.append(module)


    def run(self, ilist):
        _run_single_arg = functools.partial(_run_single,
                                            modules=self.modules,
                                            log_dir=self.log_dir)
        if self.n_job == 1:
            out = map(_run_single_arg, ilist)
        else:
            out = multiprocessing.Pool(self.n_job).map(_run_single_arg, ilist)
        print 'final output length: ', len(out)



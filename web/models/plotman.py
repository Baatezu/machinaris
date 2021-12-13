import os
import traceback

from web import app
from web.actions import worker as w


class PlottingSummary:

    def __init__(self, plottings):
        self.columns = ['worker',
                        'fork',
                        'plotter',
                        'plot_id',
                        'k',
                        'tmp',
                        'dst',
                        'wall',
                        'phase',
                        'size',
                        'pid',
                        'stat',
                        'mem',
                        'user',
                        'sys',
                        'io'
                        ]
        self.rows = []
        for plotting in plottings:
            try:
                app.logger.debug("Found worker with hostname '{0}'".format(plotting.hostname))
                displayname = w.get_worker(plotting.hostname).displayname
            except:
                app.logger.info("Unable to find a worker with hostname '{0}'".format(plotting.hostname))
                traceback.print_exc()
                displayname = plotting.hostname
            self.rows.append({
                'hostname': plotting.hostname,
                'fork': plotting.blockchain,
                'worker': displayname,
                'plotter': plotting.plotter,
                'plot_id': plotting.plot_id,
                'k': plotting.k,
                'tmp': self.strip_trailing_slash(plotting.tmp),
                'dst': self.strip_trailing_slash(plotting.dst),
                'wall': plotting.wall,
                'phase': plotting.phase,
                'size': plotting.size,
                'pid': plotting.pid,
                'stat': plotting.stat,
                'mem': plotting.mem,
                'user': plotting.user,
                'sys': plotting.sys,
                'io': plotting.io
            })
        self.calc_status()
        if True:
            self.plotman_running = True
        else:
            self.plotman_running = False

    def calc_status(self):
        if len(self.rows) > 0:
            self.display_status = "Suspended"
            for row in self.rows:
                if row['stat'] != 'STP':
                    self.display_status = "Active"
                    return
        else:
            self.display_status = "Idle"

    def strip_trailing_slash(self, path):
        if path.endswith('/'):
            return path[:-1]
        return path

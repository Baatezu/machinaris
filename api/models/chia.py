import os
import re
import traceback

from datetime import datetime

from api import app
from common.config import globals
from common.utils import converters

class FarmSummary:

    def __init__(self, cli_stdout, blockchain):
            self.plot_count = 0
            self.plots_size = 0
            for line in cli_stdout:
                if "Plot count for all" in line: 
                    self.plot_count = line.strip().split(':')[1].strip()
                elif "Total size of plots" in line: # Chia and forks
                    self.plots_size = line.strip().split(':')[1].strip()
                elif "Total space" in line: # MMX
                    self.plots_size = line.strip().split(':')[1].strip()
                elif "status" in line: 
                    self.calc_status(line.split(':')[1].strip())
                elif re.match("Total.*farmed:.*$", line):
                    self.total_coins = line.split(':')[1].strip()
                elif "Estimated network space" in line:
                    self.calc_netspace_size(line.split(':')[1].strip())
                elif "Expected time to win" in line:
                    self.time_to_win = line.split(':')[1].strip()
                elif "User transaction fees" in line:
                    self.transaction_fees = line.split(':')[1].strip()
            if not hasattr(self, 'status'):  # MMX no status yet
                self.status = ""


    def calc_status(self, status):
        self.status = status
        if self.status == "Farming":
            self.display_status = "Active"
        else:
            self.display_status = self.status

    def calc_netspace_size(self, netspace_size):
        self.netspace_size = netspace_size
        try:
            size_value, size_unit = netspace_size.split(' ')
            if float(size_value) > 1000 and size_unit == 'PiB':
                self.display_netspace_size = "{:0.3f} EiB".format(float(size_value) / 1000)
            else:
                self.display_netspace_size = self.netspace_size
        except:
            app.logger.info("Unable to split network size value: {0}".format(netspace_size))
            self.display_netspace_size = self.netspace_size

class HarvesterSummary:

    def __init__(self):
        self.status = "Harvesting" # TODO Check for harvester status in debug.log

class FarmPlots:

     def __init__(self, entries):
        self.columns = ['plot_id', 'dir', 'plot', 'create_date', 'size']
        self.rows = []
        for st_ctime, st_size, path in entries:
            if not path.endswith(".plot"):
                app.logger.info("Skipping non-plot file named: {0}".format(path))
                continue
            dir,file=os.path.split(path)
            groups = re.match("plot-k(\d+)-(\d+)-(\d+)-(\d+)-(\d+)-(\d+)-(\w+).plot", file)
            if not groups:
                app.logger.info("Invalid plot file name provided: {0}".format(file))
                continue
            plot_id = groups[7][:8]
            self.rows.append({ \
                'plot_id': plot_id, \
                'dir': dir,  \
                'file': file,  \
                'created_at': datetime.fromtimestamp(int(st_ctime)).strftime('%Y-%m-%d %H:%M:%S'), \
                'size': int(st_size) }) 

class Wallet:

    def __init__(self, cli_stdout):
        self.text = ""
        lines = cli_stdout.split('\n')
        for line in lines:
            #app.logger.info("WALLET LINE: {0}".format(line))
            if "No online" in line or \
                "skip restore from backup" in line or \
                "own backup file" in line or \
                "SIGWINCH" in line:
                continue
            self.text += line + '\n'

class Keys:

    def __init__(self, cli_stdout):
        self.text = ""
        for line in cli_stdout:
            self.text += line + '\n'

class Blockchain:

    def __init__(self, cli_stdout):
        self.text = ""
        for line in cli_stdout:
            self.text += line + '\n'

class Connections:

    def __init__(self, cli_stdout):
        self.text = ""
        for line in cli_stdout:
            self.text += line + '\n'


from PySide import QtGui
from PySide import QtCore
import pyfdtd
import dialogs
import jobs
from evalTab import EvalTab
from editTab import EditTab
from playTab import PlayTab
import simulation


# Main window for pyfdtd-gui application
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        # call base class constructor
        super(MainWindow, self).__init__()

        # init simulation
        self.simulation = pyfdtd.solver(pyfdtd.field(
            (0.4, 0.4), (0.001, 0.001)))
        self.job = jobs.Job()

        # initialize gui elements
        self.create_actions()
        self.init_gui()

    def init_gui(self):
        # set window title
        self.setWindowTitle('Pyfdtd GUI')
        self.resize(1200, 800)

        # create menu bar
        fileMenu = self.menuBar().addMenu('&File')
        scriptMenu = self.menuBar().addMenu('&Script')

        # add actions
        for action in self.fileActions:
            fileMenu.addAction(action)

        for action in self.scriptActions:
            scriptMenu.addAction(action)

        # init tab view
        tabView = QtGui.QTabWidget()
        self.setCentralWidget(tabView)

        # create edit tab
        self.editTab = EditTab(self)
        tabView.addTab(self.editTab, 'Edit')

        # create play tab
        self.playTab = PlayTab(self)
        tabView.addTab(self.playTab, 'Play')

        # create edit tab
        self.evalTab = EvalTab(self)
        tabView.addTab(self.evalTab, 'Evaluate')

        # create status bar
        statusBar = self.statusBar()
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setRange(0.0, 100.0)
        statusBar.addPermanentWidget(self.progressBar, 1)

    def create_actions(self):
        # create action list
        self.fileActions = []
        self.scriptActions = []

        # new simulation action
        self.fileActions.append(QtGui.QAction('&New', self, shortcut='Ctrl+N',
            statusTip='New simulation', triggered=self.new_simulation))

        # open simulation action
        self.fileActions.append(QtGui.QAction('&Open', self,
            shortcut='Ctrl+O', statusTip='Open simulation',
            triggered=self.open_simulation))

        # save simulation action
        self.fileActions.append(QtGui.QAction('&Save', self, shortcut='Ctrl+S',
                statusTip='Save simulation', triggered=self.save_simulation))

        # exit action
        self.fileActions.append(QtGui.QAction('&Exit', self, shortcut='Ctrl+Q',
            statusTip='Exit application', triggered=self.close))

        # open script actions
        self.scriptActions.append(QtGui.QAction('Open Script', self,
            shortcut='Ctrl+C+O', statusTip='Open evaluation script',
            triggered=self.open_script))

        # open script actions
        self.scriptActions.append(QtGui.QAction('Save Script', self,
            shortcut='Ctrl+C+S', statusTip='Save evaluation script',
            triggered=self.save_script))

    def closeEvent(self, event):
        # close eval window
        if hasattr(self, 'evalWindow'):
            self.evalWindow.close()

    def new_simulation(self):
        # new simulation callback
        def new_simulation():
            # close dialog
            self.newSimDialog.close()

            # update job
            self.job = jobs.Job()
            self.job.config['size'] = (
                    float(self.newSimDialog.xSizeEdit.text()),
                    float(self.newSimDialog.ySizeEdit.text()))
            self.job.config['delta'] = (
                    float(self.newSimDialog.deltaXEdit.text()),
                    float(self.newSimDialog.deltaYEdit.text()))

            # update edit tab
            self.editTab.update_job()
            self.editTab.update_plot()
            self.playTab.update()

        # create dialog
        self.newSimDialog = dialogs.NewSimulation()
        self.newSimDialog.okButton.clicked.connect(new_simulation)

        # get parameter
        sizeX, sizeY = self.job.config['size']
        deltaX, deltaY = self.job.config['delta']

        # set settings
        self.newSimDialog.xSizeEdit.setText(
                '{}'.format(sizeX))
        self.newSimDialog.ySizeEdit.setText(
                '{}'.format(sizeY))
        self.newSimDialog.deltaXEdit.setText(
                '{}'.format(deltaX))
        self.newSimDialog.deltaYEdit.setText(
                '{}'.format(deltaY))

        # show dialog
        self.newSimDialog.show()

    def open_simulation(self):
        # open dialog
        fname, _ = QtGui.QFileDialog.getOpenFileName(
                self, 'Open simulation')

        if fname != '':
            # load job
            self.job.load(fname)

            # create new simulation
            self.simulation = pyfdtd.solver(pyfdtd.field(
                self.job.config['size'], self.job.config['delta']))

            # update edit tab
            self.editTab.update_job()
            self.editTab.update_plot()
            self.playTab.update()

    def save_simulation(self):
        # open dialog
        fname, _ = QtGui.QFileDialog.getSaveFileName(self, 'Save simulation')

        if fname != '':
            # save job
            self.job.save(fname)

    def open_script(self):
        # open dialog
        fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open Script')

        if fname != '':
            # open file
            f = open(fname, 'r')

            # set text
            self.evalTab.inputEdit.setText(f.read())

            # close file
            f.close()

    def save_script(self):
        # open dialog
        fname, _ = QtGui.QFileDialog.getSaveFileName(self, 'Save Script')

        if fname != '':
            # open fileMenu
            f = open(fname, 'w')

            # save text
            f.write(self.evalTab.inputEdit.toPlainText())

            # close file
            f.close()

    def run_simulation(self):
        # callback functions
        def timer():
            self.progressBar.setValue(self.simulationThread.progress)

        def finished():
            self.updateTimer.stop()
            self.progressBar.setValue(100.0)

        # create simulation thread
        self.simulationThread = simulation.SimulationThread(self)

        # create timer
        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.timeout.connect(timer)
        self.simulationThread.finished.connect(finished)

        # run simulation thread
        self.updateTimer.start(100)
        self.simulationThread.start()

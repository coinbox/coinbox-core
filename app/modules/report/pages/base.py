from PySide import QtGui, QtCore

import app

import os, subprocess
import datetime

class ReportPage(QtGui.QWidget):
    def __init__(self):
        super(ReportPage, self).__init__()
        
        now = datetime.datetime.now()
        self.startDate = QtGui.QDateTimeEdit(now)
        self.startDate.setCalendarPopup(True)
        self.endDate = QtGui.QDateTimeEdit(now)
        dateSelector = QtGui.QHBoxLayout()
        dateSelector.addWidget(self.startDate)
        dateSelector.addWidget(self.endDate)
        
        try:
            dateSelector.setEnabled(self.show_date_range)
        except AttributeError:
            dateSelector.setEnabled(False)

        customLayout = self.initUI()

        buttonBox = QtGui.QDialogButtonBox()
        
        self.saveBtn = buttonBox.addButton("Save", QtGui.QDialogButtonBox.AcceptRole)
        self.saveBtn.pressed.connect(self.onSaveButton)
        
        self.printBtn = buttonBox.addButton("Print", QtGui.QDialogButtonBox.ActionRole)
        self.printBtn.pressed.connect(self.onPrintButton)

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(10)
        
        layout.addLayout(dateSelector)
        if customLayout is not None:
            layout.addLayout(customLayout)
        layout.addWidget(buttonBox)
        
        self.setLayout(layout)
        
        self.newReport()

    def initUI(self):
        return None
    
    def updateParameters(self):
        return None

    def newReport(self):
        self.path = None
        self.report = self.Report()

    def generateReport(self):
        old_params = None if self.path is None else self.report.parameters.copy()
        
        if self.show_date_range:
            self.report.parameters.update({'from': self.startDate.dateTime().toPython(),
                                           'to': self.endDate.dateTime().toPython()})
        self.updateParameters()

        if old_params is not None and self.report.parameters == old_params:
            return self.path

        filename = self.report.getFilename()

        report_dir = app.config['mod.report', 'output_dir'] or './res/report/pdf'
        path = os.path.join(report_dir, filename+".pdf")
        path = os.path.abspath(path)

        doc = self.report.generate(path)
        self.path = None if doc is None else path
        return self.path

    def viewReport(self):
        try:
            # This is only Windows
            os.startfile(file)
        except AttributeError:
            subprocess.call(["xdg-open", self.path])
            # For OSX: open <file>

    def printReport(self):
        app.log("ERROR", "Printing is not supported yet!")
        try:
            # This is only Windows
            os.startfile(file, "print")
        except AttributeError:
            # Maybe use lpr/lp/lpoption?
            subprocess.call(["xdg-open", self.path])
        return
        #http://stackoverflow.com/questions/8296021/how-to-print-pdf-file-in-qt
        # |--> http://doc.qt.nokia.com/qq/qq27-poppler.html
        # |--> http://stackoverflow.com/questions/8310681/how-to-print-image-file-from-a-printer-using-qt/8311217#8311217
        
        printer = QtGui.QPrinter()
        dlg = QtGui.QPrintDialog(printer)

    def onSaveButton(self):
        self.generateReport()
        if self.path is None:
            app.log("ERROR", "An error occured while generating report")
            return
        self.viewReport()

    def onPrintButton(self):
        self.generateReport()
        self.printReport()

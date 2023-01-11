import os
import platform
import sys
from datetime import datetime
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMenu, QMessageBox, QSizePolicy, QSystemTrayIcon
from PowerwallMonitor import PowerwallMonitor

class SettingsDialog(QDialog):
    def __init__(self, address, email, password):
      super().__init__()

      self.setWindowTitle('Powerwall Monitor Settings')

      self.address = QLineEdit(address, self)
      self.email = QLineEdit(email, self)
      self.password = QLineEdit(password, self)
      self.password.setEchoMode(QLineEdit.Password)

      buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
      buttonBox.accepted.connect(self.accept)
      buttonBox.rejected.connect(self.reject)

      layout = QFormLayout(self)
      layout.addRow('Powerwall Address', self.address)
      layout.addRow('User\'s Email', self.email)
      layout.addRow('User\'s Password', self.password)
      layout.addWidget(buttonBox)

    def get_settings(self):
      return (self.address.text(), self.email.text(), self.password.text())


class MainApp(QApplication):
  def __init__(self, args):
    super(MainApp, self).__init__(args)

    self.setQuitOnLastWindowClosed(False)

    self.setOrganizationName('pallaire')
    self.setOrganizationDomain('pallaire.com')
    self.setApplicationName('PowerwallMonitor')

    self.lastAlertDateTime = None

    # Create the icon
    self.iconNA = QIcon(os.path.join(self.get_res_path(), 'battery-na.png'))
    self.icon0 = QIcon(os.path.join(self.get_res_path(), 'battery-0.png'))
    self.icon20 = QIcon(os.path.join(self.get_res_path(), 'battery-20.png'))
    self.icon40 = QIcon(os.path.join(self.get_res_path(), 'battery-40.png'))
    self.icon60 = QIcon(os.path.join(self.get_res_path(), 'battery-60.png'))
    self.icon80 = QIcon(os.path.join(self.get_res_path(), 'battery-80.png'))
    self.icon100 = QIcon(os.path.join(self.get_res_path(), 'battery-100.png'))

    # Create the tray
    self.tray = QSystemTrayIcon()
    self.tray.setIcon(self.iconNA)
    self.tray.setVisible(True)

    # Create the menu
    self.menu = QMenu()
    self.actionCharge = QAction('Powerwall: NA')
    self.actionCharge.setEnabled(False)
    self.menu.addAction(self.actionCharge)

    self.actionSeparator = QAction('')
    self.actionSeparator.setSeparator(True)
    self.menu.addAction(self.actionSeparator)

    self.actionSettings = QAction('Settings')
    self.actionSettings.triggered.connect(self.show_settings)
    self.menu.addAction(self.actionSettings)

    self.actionQuit = QAction('Quit')
    self.actionQuit.triggered.connect(self.quit)
    self.menu.addAction(self.actionQuit)

    # Add the menu to the tray
    self.tray.setContextMenu(self.menu)

    # Settings object
    self.settings = QSettings('pallaire', 'powerwallmonitor')

    # Timer to fetch the powerwall status
    self.timer = QTimer()
    self.timer.timeout.connect(self.timer_callback)
    self.timer.setSingleShot(True)

    if self.check_settings():
      self.start_monitoring()

  def get_res_path(self):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
      return os.path.join(sys._MEIPASS, 'res')
    else:
      return os.path.join('.', 'res')

  def get_settings(self):
    return (self.settings.value('address'), self.settings.value('email'), self.settings.value('password'))

  def check_settings(self):
    (address, email, password) = self.get_settings()
    if address==None or address=='' or email==None or email=='' or password==None or password=='':
      return False
    return True

  def show_settings(self):
    (address, email, password) = self.get_settings()
    dlg = SettingsDialog(address, email, password)

    if dlg.exec():
      (address, email, password) = dlg.get_settings()
      self.settings.setValue('address', address)
      self.settings.setValue('email', email)
      self.settings.setValue('password', password)

    if self.check_settings():
      self.start_monitoring()

  def start_monitoring(self):
    (address, email, password) = self.get_settings()
    if address!=None and address!='' and email!=None and email!='' and password!=None and password!='':
      self.monitor = PowerwallMonitor(address, email, password)
      self.timer.start(500)

  def send_desktop_notification(self):
    dt = datetime.now()
    # Show alert only once per day
    if self.lastAlertDateTime == None or self.lastAlertDateTime.date() < dt.date():
      self.lastAlertDateTime = dt
      self.tray.showMessage('Powerwall Monitor', 'Your Powerwall is now fully charged', self.icon100, msecs=30000)

  def timer_callback(self):
    charge = self.monitor.get_charge()
    if charge != None: 
      label = f"Powerwall: {charge:.1f}%"
      self.tray.setToolTip(label)
      self.actionCharge.setText(label)

      if charge < 20.0:
        self.tray.setIcon(self.icon0)
      elif charge < 40.0:
        self.tray.setIcon(self.icon20)
      elif charge < 60.0:
        self.tray.setIcon(self.icon40)
      elif charge < 80.0:
        self.tray.setIcon(self.icon60)
      elif charge < 98.0:
        self.tray.setIcon(self.icon80)
      else:
        self.tray.setIcon(self.icon100)
        self.send_desktop_notification()
    else:
        self.tray.setToolTip(f"Powerwall: NA")	
        self.tray.setIcon(self.iconNA)
    self.timer.start(60000)


app = MainApp([])
app.exec()

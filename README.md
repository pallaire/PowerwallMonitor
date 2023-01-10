# PowerwallMonitor
Powerwall monitoring taskbar app using Python3 and Pyside6. It will monitor the Powerwall charge every minute, and it will send a desktop notification when your battery is full or close to full. I use this application to know when I can go plug in the car for charging without slowingdown the charging of the Powerwall. 

The application uses the Powerwall API described here: https://github.com/vloschiavo/powerwall2

Settings require:
- **Address**: The IP address of your Powerwall connected to the same network as your computer
- **Email**: The email you are using to log into the Tesla App
- **Password**: The 5 last characters of your Powerwall's serial number


![PowerwallMonitor Usage](https://github.com/pallaire/PowerwallMonitor/blob/main/rawres/screenshot.png?raw=true)
################################################################
# This is an example of using Flask to create an external,     #
# api-driven dashboard using zenApiLib.                        #
################################################################

from flask import Flask
import zenApiLib

app = Flask(__name__)

def getDevices():
    dr = zenApiLib.zenConnector(routerName='DeviceRouter')
    resp = dr.callMethod('getDevices')
    devices = resp['result']['devices']
    return devices


@app.route('/')
def drawIndex():
    devices = getDevices()
    page = '<table border="1" width="100%">'
    page += '<tr><td valign="top">Device Name</td>'
    page += '<td valign="top">IP Address</td>'
    page += '<td valign="top">UID</td>'
    page += '<td valign="top">Production State</td>'
    page += '<td valign="top">Collector</td></tr>'
    for dev in devices:
        page += '<tr><td valign="top">%s</td>' % dev['name']
        page += '<td valign="top">%s</td>' % dev['ipAddressString']
        page += '<td valign="top">%s</td>' % dev['uid']
        page += '<td valign="top">%s</td>' % dev['productionState']
        page += '<td valign="top">%s</td></tr>' % dev['collector']
    page += '</table>'
    return page


def main():
    app.run()


if __name__ == '__main__':
    main()

#!/usr/bin/env python

from flask import Flask, render_template, redirect, url_for, request, send_file
import wx
import threading
import sys
import requests
import os
import random
import math
import string

def ServerConnect(address):
    print "Address %s" % address
    r = requests.get("http://" + address + "/server/validate")
    
    if str(r.text).strip('\n') == 'remotescope-server-OK':
        return True
    else:
        return False

def RequestSession(address):
    r = requests.get("http://" + address + "/server/requestsession")
    if str(r.text) == "error-create":
        return False
    else:
        return str(r.text).strip('\n')

def DeleteSession(address,session):
    r = requests.get("http://" + address + "/server/deletesession/" + session)
    if str(r.text) == "error-delete":
        return ""
    else:
        return str(r.text).strip('\n')

def TakeScreenshot():
    global ssserver
    global sssesisionid
    global ssthread
    ssthread = threading.Timer(3.0,TakeScreenshot)
    ssthread.start()
    screen = wx.ScreenDC()
    size = screen.GetSize()
    bmp = wx.EmptyBitmap(size[0], size[1])
    mem = wx.MemoryDC(bmp)
    mem.Blit(0, 0, size[0], size[1], screen, 0, 0)
    del mem
    bmp.SaveFile('tmp/screenshot.png', wx.BITMAP_TYPE_PNG)
    r = requests.post('http://' + ssserver + '/server/upload/' + sssessionid,files={"file":open("tmp/screenshot.png","rb")})
    del bmp

def showUsage():
  print "usage: %s <server | client>" % sys.argv[0]


# Client Variables
app = None
ssthread = None
ssserver = None
sssessionid = None

# Server Variables


if not len(sys.argv) == 2:
  showUsage()
elif  sys.argv[1] == "client":
  app = wx.App()

  if not os.path.exists("tmp"):
      os.mkdir("tmp")

  while True:
      print "(C)onnect to server, (R)equest session, (B)egin screencast, (S)top screencast, (E)nd Session"
      task = raw_input(">>> ")

      if task.upper() == "C":
          ssserver = raw_input("Enter the server address: ")
          if not ServerConnect(ssserver):
              print "Unable to connect to server"
              ssserver = ""
          else:
              print "Connected to " + ssserver
      elif task.upper() == "R":
          sssessionid = RequestSession(ssserver)
          if not sssessionid:
              print "Unable to establish session with " + ssserver
          else:
              print "Session open with server: " + sssessionid
      elif task.upper() == "B":
          TakeScreenshot()
          print "Starting screencast"
      elif task.upper() == "S":
          ssthread.cancel()
          print "Stopping screencast"
      elif task.upper() == "E":
          returnval = DeleteSession(ssserver,sssessionid)
          if not returnval:
              print "Unable to end session " + sssessionid + " with server " + ssserver
          else:
              print "Ended session " + sssessionid + " with server " + ssserver
              sssessionid = ""
              ssserver = ""
              sys.exit()
elif sys.argv[1] == "server":
  app = Flask(__name__)

  sessionidlen = 5

  if not os.path.exists("sessions"):
    os.mkdir("sessions")

  @app.route("/client/")
  @app.route("/client")
  def clientList():
    sessionlist = os.listdir("sessions/")
    return render_template("clientlist.html",sessionlist=sessionlist)

  @app.route("/client/<sessionid>")
  def clientView(sessionid):
    return render_template("clientview.html",sessionid=sessionid)

  @app.route("/client/<sessionid>/screenshot.png")
  def returnclientViewImage(sessionid):
    return send_file("sessions/" + sessionid + "/screenshot.png")

  @app.route("/server")
  @app.route("/server/")
  def serverRoot():
    return redirect(url_for("client"))

  @app.route("/server/validate")
  def validateServer():
    return "remotescope-server-OK"

  @app.route("/server/requestsession")
  def sessionRequest():
    try:
      newsessionid = str(int(random.random() * (math.pow(10,sessionidlen)))).zfill(sessionidlen)
      os.mkdir("sessions/" + newsessionid)
      return newsessionid
    except:
      return "error-create"

  @app.route("/server/deletesession/<sessionid>")
  def sessionDelete(sessionid):
    try:
      os.remove("sessions/" + sessionid + "/screenshot.png")
      os.rmdir("sessions/" + sessionid)
      return sessionid
    except:
      return "error-delete" 

  @app.route("/server/upload/<sessionid>", methods=["GET","POST"])
  def uploadSessionImage(sessionid):
    if request.method == "POST":
      try:
        file = request.files['file']
        if file and file.filename == "screenshot.png":
          file.save("sessions/" + sessionid + "/" + file.filename)
          return "file-uploaded"
        else:
          return "upload-invalid"
      except:
        return "upload-error"        
    else:
      return redirect(url_for("client"))

  app.run(host="0.0.0.0",port=8080)
else:
  showUsage()

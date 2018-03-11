import os
import subprocess
import re
import ctypes
import time
import binascii
import fileinput
import sys
import shutil
import getpass
import fileinput
import logging
import logging.handlers
from time import gmtime, strftime

seperator = "=" * 80
LogDict = []

def InitLoger(env, LoggerName, formatTmp):
  LogFilePath = env["logFilePath"] + env["logFileName"]
  logging.basicConfig(level=logging.DEBUG,
                      format=formatTmp,
                      datefmt='%Y-%m-%d %H:%M',
                      handlers = [logging.FileHandler(LogFilePath, 'w', 'utf-8'),])

  ServerHandler = logging.handlers.SocketHandler ('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
  console = logging.StreamHandler()
  Log = logging.getLogger(LoggerName)
  Log.addHandler(console)
  Log.addHandler(ServerHandler)
  return Log

def RestoreFile(RestoreInfo):

  # Replace string "!import SioXXXPkg/Package.dsc" and "!import SioXXXPkg/Package.fdf" to SioDummyPkg
  replaceFirstLine(RestoreInfo["dscPath"], RestoreInfo["SioDummyPkgDsc"], RestoreInfo["dscString"])
  replaceFirstLine(RestoreInfo["fdfPath"], RestoreInfo["SioDummyPkgfdf"], RestoreInfo["fdfString"])

  # Move SioXXXPkg from ["projectRootPath"] to ["SioNotBuiltPath"]
  SioList = getSioList(RestoreInfo["projectRootPath"], "^Sio.*Pkg$")
  for line in SioList:
    if "SioDummyPkg" in line:
      continue
    elif os.path.exists(RestoreInfo["projectRootPath"] + line):
      shutil.move(RestoreInfo["projectRootPath"] + line, RestoreInfo["SioNotBuiltPath"])
    else:
      Print("End of move file to allSio2 folder\n")

  # Move SioXXXPkg from ["SioBuiltPath"] to ["SioNotBuiltPath"]
  SioList = getSioList(RestoreInfo["SioBuiltPath"], "^Sio.*Pkg$")
  for line in SioList:
    if os.path.exists(RestoreInfo["SioBuiltPath"] + line):
      shutil.move(RestoreInfo["SioBuiltPath"] + line, RestoreInfo["SioNotBuiltPath"])

  # Remove SioXXXPkg.fd in ["BinaryRenamePath"]
  SioList = getSioList(RestoreInfo["BinaryRenamePath"], "^Sio.*Pkg.fd$")
  for line in SioList:
    if os.path.exists(RestoreInfo["BinaryRenamePath"] + line):
      os.remove(RestoreInfo["BinaryRenamePath"] + line)

def executeBatchFile(path, RestoreInfo):
  try:
      p = subprocess.Popen(path)
      p.wait()
  except KeyboardInterrupt:
      print("Program is interrupted!\n")
      RestoreFile(RestoreInfo)
      sys.exit(0)


def replaceFirstLine(path, s, TargetStr):

#  SioDummyPkgDsc = "!import SioDummyPkg/Package.dsc"
#  SioDummyPkgFdf = "!import SioDummyPkg/Package.fdf"

  with fileinput.FileInput(path, inplace=True) as f:
    for line in f:
      print(line.replace(TargetStr, s), end="")

#  content = ""
#  with open(path, "r") as f:
#    content = f.read()

#  print (path, s)

#  content = content.splitlines()
#  content[33] = s
#  content = "\n".join(content)

#  with open(path, "w") as f:
#    f.write(content)

def makeLogFileFunction(path):

  def f(s):
    with open(path, "a") as f:
      f.write(s + "\n")

  return f



def initialize(env):
  # rename existing binary file
  if os.path.exists(env["binaryName"]):
    os.rename(env["binaryName"], env["binaryName"] + "Org.fd")

  # create log file's directory paht
  if not os.path.exists(env["logFilePath"]):
    os.makedirs(env["logFilePath"])

  # create error log file's directory paht
  if not os.path.exists(env["ErrorLogFilePath"]):
    os.makedirs(env["ErrorLogFilePath"])

  # create before-built folder
  if not os.path.exists(env["sioNotBuiltPath"]):
    os.makedirs(env["sioNotBuiltPath"])

  # create after-built folder
  if not os.path.exists(env["sioBuiltPath"]):
    os.makedirs(env["sioBuiltPath"])

def getSioList(path, format):
  sioList = []
  regex = re.compile (format)
  for d in os.listdir(path) :
    if regex.search(d) :
      sioList.append(d)

  return sioList

def CreateRestoreInfo(env, dscPath, fdfPath, dscString, fdfString, SioDummyPkgDsc, SioDummyPkgfdf):
  RestoreInfo = {}
  RestoreInfo["dscPath"] = dscPath
  RestoreInfo["fdfPath"] = fdfPath
  RestoreInfo["dscString"] = dscString
  RestoreInfo["fdfString"] = fdfString
  RestoreInfo["SioDummyPkgDsc"] = SioDummyPkgDsc
  RestoreInfo["SioDummyPkgfdf"] = SioDummyPkgfdf
  RestoreInfo["projectRootPath"] = env["sioNotBuiltPath"]
  RestoreInfo["SioBuiltPath"] = env["sioBuiltPath"]
  RestoreInfo["SioNotBuiltPath"] = env["sioNotBuiltPath"]
  RestoreInfo["BinaryRenamePath"] = env["binaryRenamePath"]
  RestoreInfo["projectRootPath"] = env["projectRootPath"]
  return RestoreInfo

def ToolKeyCheck():
  user = getpass.getuser()
  pwd = getpass.getpass()
  ToolKey = "123"

  if pwd != ToolKey:
    print("Pleas pay $5 to bank account : XXXX-XXXX-XXXX to unlock this compile tool!\n")
    sys.exit()

def ShowLog(LogFilePath):
  count = 0
  if not len(LogDict) == 0:
    LogDict.clear()

  if os.path.exists(LogFilePath):
    with open(LogFilePath) as f:
      for line in f:
        if "Sio" in line:
          print("[%02d] %s" %(count, line), end="")
#          StartPosition = line.find("Sio")
#          EndPostion = line.find("Pkg")
#          LogDict.append(line[StartPosition:EndPostion+3])
          count += 1
        else:
          print(line, end="")
#    print(open(LogFilePath).read())
    sys.exit()
  else:
    print("Log File isn't exist!\n")
    sys.exit()

def CleanLogAndBinaryFile(LogFilePath, ErrorLogFilePath, binaryRenamePath):
  if os.path.exists(LogFilePath):
    os.remove(LogFilePath)
    shutil.rmtree(ErrorLogFilePath)
    SioList = getSioList(binaryRenamePath, "^Sio.*Pkg.fd$")
    for line in SioList:
      if os.path.exists(binaryRenamePath + line):
        os.remove(binaryRenamePath + line)
    sys.exit()
  else:
    print("Clean Log File and bin was failed!\n")
    sys.exit()

def ShowErrorLog (ErrorLogFilePath, argv):
  Buffer = []
  count = 0
  if os.path.exists(ErrorLogFilePath) and (len(argv) < 3):
    SioList = getSioList(ErrorLogFilePath, "^Sio.*Pkg.log$")
    for line in SioList:
      print(line + "\n" + seperator)
      Buffer = TextFilter (line[0:-3], ErrorLogFilePath + line)
      for line2 in Buffer:
        print(line2, end="")
      print("\n")
      input()
  elif len(argv) >= 3:
    with open("BIOS/SioLog.txt") as f:
      for line in f:
        if "Sio" in line:
          StartPosition = line.find("Sio")
          EndPostion = line.find("Pkg")
          LogDict.append(line[StartPosition:EndPostion+3])
    tmp = int(argv[2])

    try:
      with open(ErrorLogFilePath + LogDict[tmp] + ".log") as f:
        for line in f:
          Buffer = TextFilter (LogDict[tmp], ErrorLogFilePath + LogDict[tmp] + ".log")
      print(LogDict[tmp] + "\n" + seperator)
      for line in Buffer:
        print(line, end="")
    except:
      print("Error Log File isn't exist!\n")
    sys.exit()
  else:
    print("Error Log File isn't exist!\n")
  sys.exit()

def OpenDevice (env):
  SioNameList = getSioList(env["sioNotBuiltPath"], "^Sio.*Pkg$")
  for name2 in SioNameList:
    with fileinput.FileInput(env["sioNotBuiltPath"] + name2 + "/Package.dsc", inplace=True) as file2:
      for line in file2:
        print(line.replace("|FALSE", "|TRUE"), end='')

    with fileinput.FileInput(env["sioNotBuiltPath"] + name2 + "/" + name2 + ".dec", inplace=True) as file2:
      for line in file2:
        print(line.replace("|FALSE", "|TRUE"), end='')
  sys.exit()

def OpenDeviceEx (env):
  SioNameList = getSioList(env["sioNotBuiltPath"], "^Sio.*Pkg$")
  for name2 in SioNameList:
     EndFlag = False;
     with fileinput.FileInput(env["sioNotBuiltPath"] + name2 + "/Package.dsc", inplace=True) as file2:
       for line in file2:
         if "# End Entry" in line:
           EndFlag = True;
         if not EndFlag:
           print(line.replace("0x00, UINT16", "0x01, UINT16"), end="")
         else:
           print(line, end="")
  sys.exit()

def ArgvCheck(argv, env):

  LogFilePath = env["logFilePath"] + env["logFileName"]
  ErrorLogFilePath = env["ErrorLogFilePath"]
  binaryRenamePath = env["binaryRenamePath"]

  if len(argv) < 2:
    pass
  else:
    if argv[1] == "log":
      ShowLog (LogFilePath)
    elif argv[1] == "clean":
      CleanLogAndBinaryFile (LogFilePath, ErrorLogFilePath, binaryRenamePath)
    elif argv[1] == "err":
      ShowErrorLog (ErrorLogFilePath, argv)
    elif argv[1] == "op":
      OpenDevice (env)
    elif argv[1] == "opex":
      OpenDeviceEx (env)
    else:
      print("Unknow commad!\n")
      sys.exit()

def TextFilter (name, path):
  Buffer=[]
  with open(path, 'r') as f:
    count = 0
    for line in f:
      count += 1
      if (name[0:-3] in line and (not "Building" in line)): #and (("error" in line) or ("warning" in line)):
        Buffer.append("[%d] %s" %(count, line))
  return Buffer

def getEnvironment(configPath):
  d = { "projectRootPath"  : "../"
      , "binaryRenamePath" : "BIOS/"
      , "sioNotBuiltPath"  : "../allSio2/"
      , "sioBuiltPath"     : "../allSio2Built/"
      , "logFilePath"      : "BIOS/"
      , "ErrorLogFilePath" : "BIOS/ErrorLog/"
      , "binaryName"       : "BIOS/Kabylake.fd"
      , "logFileName"      : "SioLog.txt"
      , "batchFile"        : "ProjectBuildUefi64.bat"
      }
#  print (seperator)
#  print ("current environment:")
#  for k in d:
#    print (k + ":" + d[k])
#  print (seperator)

  d["logFileFunc"] = makeLogFileFunction(d["logFilePath"] + d["logFileName"])

  return d

def main():

#  ToolKeyCheck()

  SioDummyPkgDsc = "!import SioDummyPkg/Package.dsc"
  SioDummyPkgfdf = "!import SioDummyPkg/Package.fdf"

  env = getEnvironment("compileListConfig.conf")

  ArgvCheck(sys.argv, env)
  initialize(env)
#  Log = InitLoger(env, "Logger1", "%(asctime)s %(message)s")
  sioNames = getSioList(env["sioNotBuiltPath"], "^Sio.*Pkg$")

  successCount = 0
  failedCount = 0
  notFoundCount = 0

  env["logFileFunc"](seperator);
  env["logFileFunc"](strftime ("%Y-%m-%d %H:%H:%S", gmtime()))

  if len(sioNames) == 0:
    print("Not found any SioXXXPkg in allSio2 folder\n")
    sys.exit()

#  Log.info("======= START =======")

  for name in sioNames:

    # move the sio package to project root
    fromPath = env["sioNotBuiltPath"] + name
    toPath = env["projectRootPath"] + name

    print ("move " + fromPath + " to " + toPath)
    try:
      os.rename (fromPath, toPath)
    except:
      env["logFileFunc"]("notfound: " + name)
      notFoundCount += 1
      continue

    # modify dsc and fdf file of project board package
    dscPath = "Project.dsc"
    fdfPath = "Project.fdf"
    dscString = "!import " + name + "/Package.dsc"
    fdfString = "!import " + name + "/Package.fdf"

    # Create RestoreInfo Table, it used to restore data when "Ctrl+C" event is trigger
    RestoreInfo = CreateRestoreInfo(env, dscPath, fdfPath, dscString, fdfString, SioDummyPkgDsc, SioDummyPkgfdf)

    replaceFirstLine(dscPath, dscString, SioDummyPkgDsc)
    replaceFirstLine(fdfPath, fdfString, SioDummyPkgfdf)

    # compile
    executeBatchFile(env["batchFile"], RestoreInfo)

    replaceFirstLine(dscPath, SioDummyPkgDsc, dscString)
    replaceFirstLine(fdfPath, SioDummyPkgfdf, fdfString)


    # if the target binary exists, rename it to Sioname + binaryname
    SioKey = 0
    if os.path.exists(env["binaryName"]):
      fromPath = env["binaryName"]
      toPath = env["binaryRenamePath"] + name + ".fd"
      os.rename(fromPath, toPath)
      env["logFileFunc"](" success: " + name)
#      LogDict[SioKey] = LogDict.append(name)
#      SioKey +=1
#      Log.info("success: " + name)
      successCount += 1
    else:
      env["logFileFunc"](" failed: " + name)
#      Log.info("failed: " + name)
#      LogDict[SioKey] = LogDict.append(name)
#      SioKey +=1
      failedCount += 1
      try:
        os.rename ("log.txt", env["ErrorLogFilePath"] + name + ".log")
      except:
        pass

    # put the compiled sio package to built path
    fromPath = env["projectRootPath"] + name
    toPath = env["sioBuiltPath"] + name
    os.rename (fromPath, toPath)

  for name in sioNames:
    shutil.move(env["sioBuiltPath"] + name,  env["sioNotBuiltPath"])

  env["logFileFunc"](" success: " + str(successCount))
  env["logFileFunc"](" failed: " + str(failedCount))
  env["logFileFunc"](" not found: " + str(notFoundCount))
  env["logFileFunc"](strftime ("%Y-%m-%d %H:%H:%S", gmtime()))
  env["logFileFunc"](seperator)

#  Log.info("======== END ========")


if __name__ == "__main__":
  main()

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
import configparser
from time import gmtime, strftime
from colorama import init
from colorama import Fore, Back, Style

seperator = "=" * 80
LogDict = []

class NewConfigParser(configparser.ConfigParser):

  def optionxform(self, optionstr):
      return optionstr

def InitLoger(env, LoggerName, formatTmp):
  LogFilePath = env["LogFilePath"] + env["LogFileName"]
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

  # Move SioXXXPkg from ["ProjectRootPath"] to ["SioNotBuiltPath"]
  SioList = getSioList(RestoreInfo["ProjectRootPath"], "^Sio.*Pkg$")
  for line in SioList:
    if "SioDummyPkg" in line:
      continue
    elif os.path.exists(RestoreInfo["ProjectRootPath"] + line):
      shutil.move(RestoreInfo["ProjectRootPath"] + line, RestoreInfo["SioNotBuiltPath"])
    else:
      Print(Fore.RED + "End of move file to allSio2 folder\n")

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
      print(Fore.RED + "Program is interrupted!\n")
      RestoreFile(RestoreInfo)
      sys.exit(0)


def replaceFirstLine(path, s, TargetStr):

  with fileinput.FileInput(path, inplace=True) as f:
    for line in f:
      print(line.replace(TargetStr, s), end="")

def makeLogFileFunction(path):

  def f(s):
    with open(path, "a") as f:
      f.write(s + "\n")

  return f

def initialize(env):

  #On Windows, calling init() will filter ANSI escape sequences out of any text sent to stdout or stderr, and replace them with equivalent Win32 calls.
  init ()

  # rename existing binary file
  if os.path.exists(env["BinaryRenamePath"] + env["BinaryFileName"]):
    os.rename(env["BinaryRenamePath"] + env["BinaryFileName"], env["BinaryRenamePath"] + env["BinaryFileName"] + "Org.fd")

  # create log file's directory path
  if not os.path.exists(env["LogFilePath"]):
    os.makedirs(env["LogFilePath"])

  # create error log file's directory path
  if not os.path.exists(env["ErrorLogFilePath"]):
    os.makedirs(env["ErrorLogFilePath"])

  # create before-built folder
  if not os.path.exists(env["SioNotBuiltPath"]):
    os.makedirs(env["SioNotBuiltPath"])

  # create after-built folder
  if not os.path.exists(env["SioBuiltPath"]):
    os.makedirs(env["SioBuiltPath"])

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
  RestoreInfo["ProjectRootPath"] = env["SioNotBuiltPath"]
  RestoreInfo["SioBuiltPath"] = env["SioBuiltPath"]
  RestoreInfo["SioNotBuiltPath"] = env["SioNotBuiltPath"]
  RestoreInfo["BinaryRenamePath"] = env["BinaryRenamePath"]
  RestoreInfo["ProjectRootPath"] = env["ProjectRootPath"]
  return RestoreInfo

def ShowLog(LogFilePath):
  count = 0
  ColorDict = {
    0 : Fore.RED,
    1 : Fore.GREEN,
    2 : Fore.BLUE,
    3 : Fore.MAGENTA,
    4 : Fore.CYAN,
    5 : Fore.WHITE,
  }

  if not len(LogDict) == 0:
    LogDict.clear()

  if os.path.exists(LogFilePath):
    with open(LogFilePath) as f:
      for line in f:
        if "Sio" in line:
          if "failed" in line:
            StartPos = line.find("failed")
            EndPos = StartPos + len("failed")
            TmpStr = "  " + Fore.RED + line[StartPos:EndPos] + Fore.RESET + line[EndPos:-1] + "\n"
            print(Fore.MAGENTA + "[%02d]" %(count) + Fore.RESET + TmpStr, end="")
          else:
            print(Fore.MAGENTA + "[%02d]" %(count) + Fore.RESET + line, end="")
          count += 1
        else:
          print(line, end="")
    sys.exit()
  else:
    print(Fore.RED + "Log File isn't exist!\n")
    sys.exit()

def CleanLogAndBinaryFile(LogFilePath, ErrorLogFilePath, BinaryRenamePath):
  if os.path.exists(LogFilePath):
    os.remove(LogFilePath)
    shutil.rmtree(ErrorLogFilePath)
    SioList = getSioList(BinaryRenamePath, "^Sio.*Pkg.fd$")
    for line in SioList:
      if os.path.exists(BinaryRenamePath + line):
        os.remove(BinaryRenamePath + line)
    sys.exit()
  else:
    print(Fore.RED + "Clean Log File and bin was failed!\n")
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
    try:
      with open("BIOS/SioLog.txt") as f:
        for line in f:
          if "Sio" in line:
            StartPosition = line.find("Sio")
            EndPostion = line.find("Pkg")
            LogDict.append(line[StartPosition:EndPostion+3])
      tmp = int(argv[2])
    except:
      print(Fore.RED + "SioLog File isn't exist!\n")
      sys.exit()

    try:
      with open(ErrorLogFilePath + LogDict[tmp] + ".log") as f:
        for line in f:
          Buffer = TextFilter (LogDict[tmp], ErrorLogFilePath + LogDict[tmp] + ".log")
      print(LogDict[tmp] + "\n" + seperator)
      for line in Buffer:
        print(line, end="")
    except:
      print(Fore.RED + "Error Log File isn't exist!\n")
    sys.exit()
  else:
    print(Fore.RED + "Error Log File isn't exist!\n")
  sys.exit()

def OpenDevice (env):
  SioNameList = getSioList(env["SioNotBuiltPath"], "^Sio.*Pkg$")
  for name2 in SioNameList:
    with fileinput.FileInput(env["SioNotBuiltPath"] + name2 + "/Package.dsc", inplace=True) as file2:
      for line in file2:
        print(line.replace("|FALSE", "|TRUE"), end='')

    with fileinput.FileInput(env["SioNotBuiltPath"] + name2 + "/" + name2 + ".dec", inplace=True) as file2:
      for line in file2:
        print(line.replace("|FALSE", "|TRUE"), end='')
  sys.exit()

def OpenDeviceEx (env):
  SioNameList = getSioList(env["SioNotBuiltPath"], "^Sio.*Pkg$")
  for name2 in SioNameList:
     EndFlag = False;
     with fileinput.FileInput(env["SioNotBuiltPath"] + name2 + "/Package.dsc", inplace=True) as file2:
       for line in file2:
         if "# End Entry" in line:
           EndFlag = True;
         if not EndFlag:
           print(line.replace("0x00, UINT16", "0x01, UINT16"), end="")
         else:
           print(line, end="")
  sys.exit()

def ShowHelpInfo():

  HelpInfo = "Usage: " + Fore.YELLOW + "CompileCodeList.py [Option] ... [ log | clean | err | op | opex | bu ] [arg] ...\n" + Fore.RESET + \
"Options and arguments (and corresponding environment variables):\n" + \
Fore.RED + "log          " + Fore.RESET + ":List build report summary\n" + \
Fore.RED + "clean        " + Fore.RESET + ":Delete log, errlog and SioXXXPkg.bin\n" + \
Fore.RED + "err <Index>  " + Fore.RESET + ":List build error report step by step, <Index> is a optional argument,\n" + \
"              it used to view the specified SIO error report \n" + \
Fore.RED + "op           " + Fore.RESET + ":Turn on SIO 5.X all device to TRUE\n" + \
Fore.RED + "opex         " + Fore.RESET + ":Turn on SIO 5.0 all device to TRUE\n" + \
Fore.RED + "bu           " + Fore.RESET + ":Start to build SIO\n" + \
"###########################################################################################\n" + \
"2018/05/11 released.\n" + \
"Author   : " + Fore.CYAN + "Renjie Tsai\n" + Fore.RESET + \
"Maintain : " + Fore.CYAN + "Ichan Chen\n" + Fore.RESET

  print(Fore.RESET)
  print(HelpInfo)

def ArgvCheck(argv, env):

  LogFilePath = env["LogFilePath"] + env["LogFileName"]
  ErrorLogFilePath = env["ErrorLogFilePath"]
  BinaryRenamePath = env["BinaryRenamePath"]

  #On Windows, calling init() will filter ANSI escape sequences out of any text sent to stdout or stderr, and replace them with equivalent Win32 calls.
  init()

  if len(argv) < 2:
    ShowHelpInfo ()
    sys.exit()
  else:
    if argv[1] == "log":
      ShowLog (LogFilePath)
    elif argv[1] == "clean":
      CleanLogAndBinaryFile (LogFilePath, ErrorLogFilePath, BinaryRenamePath)
    elif argv[1] == "err":
      ShowErrorLog (ErrorLogFilePath, argv)
    elif argv[1] == "op":
      OpenDevice (env)
    elif argv[1] == "opex":
      OpenDeviceEx (env)
    elif argv[1] == "bu":
      pass
    else:
      print(Fore.RED + "Invalid commad!\n")
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

def ConfFileTextAlign(Path):

  MaxStrLength = 0
  TempLenght = 0
  Buffer = []
  TmpStrSplit = []

  config = NewConfigParser(configparser.ConfigParser())
  config.read(Path)
  for line in config.sections():
    Section = line
    for line2 in config[Section]:
      TempLenght = len(line2)
      if TempLenght > MaxStrLength:
        MaxStrLength = TempLenght

  MaxStrLength += 2

  with open(Path, "r") as f:
    for line in f:
      StrLengthCount = 0
      TmpStrSplit.clear()
      NewStr = ""
      if ":" in line:
        TmpStrSplit = line.split()
        for line2 in TmpStrSplit:
          StrLengthCount += len(line2)
          if line2 == ":":
            NewStr += " " * (MaxStrLength - StrLengthCount) + " " + line2 + " "
          else:
            NewStr += line2
        Buffer.append(NewStr)

      else:
        Buffer.append(line)

  f2 = open(Path, 'w')
  for line in Buffer:
    if ":" in line:
      f2.write("  " + line + "\n")
    else:
      f2.write(line)


def getEnvironment(ConfigPath):
  CurrentSetting = {}
  defaultSetting = {
  "Paths"    : {
                     "ProjectRootPath"  : "../"
                   , "BinaryRenamePath" : "BIOS/"
                   , "SioNotBuiltPath"  : "../allSio2/"
                   , "SioBuiltPath"     : "../allSio2Built/"
                   , "LogFilePath"      : "BIOS/"
                   , "ErrorLogFilePath" : "BIOS/ErrorLog/"
                 },
  "FileName" : {
                     "BinaryFileName"   : "Kabylake.fd"
                   , "LogFileName"      : "SioLog.txt"
                   , "BatchFileName"    : "ProjectBuildUefi64.bat"
                 }
  }

  if os.path.exists(ConfigPath):
    config = NewConfigParser(configparser.ConfigParser())
    config.read(ConfigPath)
    for Section in config.sections():
      for Index in config.options(Section):
        CurrentSetting[Index] = config[Section][Index]
    CurrentSetting["LogFileFunc"] = makeLogFileFunction(CurrentSetting["LogFilePath"] + CurrentSetting["LogFileName"])
  else:
    f = open(ConfigPath, "w")
    for line in defaultSetting:
      f.write("[" + line + "]" + "\n")
      for line2 in defaultSetting[line]:
         f.write("  " + line2 + " : " + defaultSetting[line][line2] + "\n")
      f.write("\n")
    f.close()
    for Section in defaultSetting:
      for Index in defaultSetting[Section]:
        CurrentSetting[Index] = defaultSetting[Section][Index]
    CurrentSetting["LogFileFunc"] = makeLogFileFunction(defaultSetting["Paths"]["LogFilePath"] + defaultSetting["FileName"]["LogFileName"])
    ConfFileTextAlign(ConfigPath)

  return CurrentSetting

def main():

  SioDummyPkgDsc = "!import SioDummyPkg/Package.dsc"
  SioDummyPkgfdf = "!import SioDummyPkg/Package.fdf"

  env = getEnvironment("CompileListConfig.conf")

  ArgvCheck(sys.argv, env)
  initialize(env)
  SioNames = getSioList(env["SioNotBuiltPath"], "^Sio.*Pkg$")

  successCount = 0
  failedCount = 0
  notFoundCount = 0

  env["LogFileFunc"](seperator);
  env["LogFileFunc"](strftime ("%Y-%m-%d %H:%H:%S", gmtime()))

  if len(SioNames) == 0:
    print(Fore.RED + "Not found any SioXXXPkg in allSio2 folder\n")
    sys.exit()

  for name in SioNames:

    # move the sio package to project root
    fromPath = env["SioNotBuiltPath"] + name
    toPath = env["ProjectRootPath"] + name

    print ("move " + fromPath + " to " + toPath)
    try:
      os.rename (fromPath, toPath)
    except:
      env["LogFileFunc"]("notfound: " + name)
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
    executeBatchFile(env["BatchFileName"], RestoreInfo)

    replaceFirstLine(dscPath, SioDummyPkgDsc, dscString)
    replaceFirstLine(fdfPath, SioDummyPkgfdf, fdfString)

    # if the target binary exists, rename it to Sioname + BinaryFileName
    if os.path.exists(env["BinaryRenamePath"] + env["BinaryFileName"]):
      fromPath = env["BinaryRenamePath"] + env["BinaryFileName"]
      toPath = env["BinaryRenamePath"] + name + ".fd"
      os.rename(fromPath, toPath)
      env["LogFileFunc"](" success: " + name)
      successCount += 1
    else:
      env["LogFileFunc"](" failed: " + name)
      failedCount += 1
      try:
        os.rename ("log.txt", env["ErrorLogFilePath"] + name + ".log")
      except:
        pass

    # put the compiled sio package to built path
    fromPath = env["ProjectRootPath"] + name
    toPath = env["SioBuiltPath"] + name
    os.rename (fromPath, toPath)

  for name in SioNames:
    shutil.move(env["SioBuiltPath"] + name,  env["SioNotBuiltPath"])

  env["LogFileFunc"](" success: " + str(successCount))
  env["LogFileFunc"](" failed: " + str(failedCount))
  env["LogFileFunc"](" not found: " + str(notFoundCount))
  env["LogFileFunc"](strftime ("%Y-%m-%d %H:%H:%S", gmtime()))
  env["LogFileFunc"](seperator)

  #To stop using colorama before your program exits
  deinit()

if __name__ == "__main__":
  main()

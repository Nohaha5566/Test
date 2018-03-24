import os
import subprocess
import re
import ctypes
import time
import binascii
import shutil
import fileinput
import uuid
import codecs
from stat import *

def GenerateGuid():
  return uuid.uuid4()

def GetFileList(Regex):

  Buffer = []

  regex = re.compile (Regex)
  for line in os.listdir("."):
    if regex.search(line):
      Buffer.append(str(line))
  return Buffer

def DepthSearchFile():
  #This function will return dirPath, dirNames, and fileNames
  return os.walk()

def RenameFile(Dst):
  return os.rename(Dst)

def CopyFile(Src, Dst):
  return shutil.copy2(Src, Dst)

def MoveFile(Src, Dst):
  return shutil.move(Src, Dst)

def DeleteFile(Dst):
  return os.remove(Dst)

def CopyFolder(Src, Dst):
  return shutil.copytree(Src, Dst)

def DeleteFolder(Src):
  return shutil.rmtree(Src)

def CopyFileContent(Src, Dst):
  return shutil.copyfile(Src, Dst)

def OverrideFile(SrcFilePathList, DstPathList):
#  SrcFilePathList = {
#    "File1": "",
#    "File2": "",
#    "File3": "",
#  }

#  DstPathList = {
#    "File1": "",
#    "File2": "",
#    "File3": "",
#  }

  for line in SrcFilePathList:
     mode = os.stat(SrcFilePathList[line])[ST_MODE]
     if S_ISDIR(mode):
       if (os.path.exists(DstPathList[line])):
         shutil.rmtree(DstPathList[line])
         shutil.copytree(SrcFilePathList[line], DstPathList[line])
     elif S_ISREG(mode):
       if (os.path.isfile(DstPathList[line])):
        os.remove(DstPathList[line])
        shutil.copy2(SrcFilePathList[line], DstPathList[line])
     else:
       print("End of line\n!")

def RelplaceString(FilePath, BeforStr, AfterStr):
  if os.path.exists(FilePath):
    with fileinput.FileInput(FilePath, inplace=True) as f2:
      for line in f2:
        print(line.replace(BeforStr, AfterStr), end="")

def InsertStringToFile(FilePath, KeyWord, String):

  Buffer = []

  with fileinput.FileInput(FilePath, inplace=False) as file2:
     for line in file2:
       if KeyWord in line[0:-1]:
         Buffer.append(line + String)
       else:
         Buffer.append(line)

  f = open(FilePath, 'w')
  for line in Buffer:
    f.write(line)
  f.close()

def InsertStringToUni(Path, KeyWordStr, TargetStr):

  Buffer = []

  with codecs.open(Path, encoding='utf-16') as file:
    for line in file:
      if KeyWordStr in line:
        Buffer.append(line + TargetStr)
      else:
        Buffer.append(line)

  with codecs.open(Path, 'w', encoding='utf-16') as f:
    for line in Buffer:
      f.write(line)

def DeleteStringFromFile(Path, KeyWord):

  Buffer = []
  flag = False

  with open(Path) as f2:
    for line in f2:
      if KeyWord in line:
        Buffer.append(line)
        flag = True
      else:
        if not flag:
          Buffer.append(line)
        else:
          flag = False
  f2 = open(Path, 'w')
  for line in Buffer:
    f2.write(line)
  f2.close()

def DeleteStringFromFileEx(FilePath, KeyWord, NumRmLine):

  Buffer = []
  flag = True

  with fileinput.FileInput(FilePath, inplace=False) as file2:
     for line in file2:
       if KeyWord in line:
         NumRmLine -= 1
         flag = False
       elif NumRmLine == 0:
         flag = True
         Buffer.append(line)
       else:
         if flag:
           Buffer.append(line)
         else:
           NumRmLine -= 1

  f = open(FilePath, 'w')

  for line in Buffer:
    f.write(line)
  f.close()

def ModifyInfFileGuid(FilePath):

  NewStr = ""
  Buffer = []
  GuidStrLength = 36
  regex = re.compile("\w{8}-\w{4}-\w{4}-\w{4}-\w{12}")

  with fileinput.FileInput(FilePath, inplace=False) as f:
    for line in f:
      if regex.search(line):
        FirstStrEndPos = regex.search(line).start()
        NewStr = line[0:FirstStrEndPos] + str(GenerateGuid()) + line[FirstStrEndPos+GuidStrLength:-1]
        Buffer.append(NewStr + "\n")
      else:
        Buffer.append(line)

  TmpFile = open(FilePath, 'w')
  for line in Buffer:
    TmpFile.write(line)
  TmpFile.close()

def StringAlign(Path, SampleStr, Format):

  regex = re.compile(Format)
  Buffer = []
  Flag = False
  Space = " "
  Length = 0
  Index = 0
  NewStr = ""
  SplitList = []

  for sector in SampleStr.split():
    SplitList.append(SampleStr.find(sector))

  with open(Path, 'r') as f:
    for line in f:
      if regex.search(line) and (len(line) <= len(SampleStr)):
        Flag = True
        for ArgPos in SplitList:
          Length = len(NewStr)
          NewStr += Space*(ArgPos - Length) + line.split()[Index]
          Index += 1
        Buffer.append(NewStr + "\n")

      if not Flag:
        Buffer.append(line)
      else:
        Flag = False

  f = open(Path, 'w')
  for line in Buffer:
    f.write(line)
  f.close()

def main():
  """
   WorkSpace in here!
  """

# GetFileList(Regex)
  #
  # File System
  #
#  RenameFile(Dst):
#  CopyFile(Src, Dst):
#  MoveFile(Src, Dst):
#  DeleteFile(Dst):
#  CopyFolder(Src, Dst):
#  DeleteFolder(Src):
#  CopyFileContent(Src, Dst):
#  OverrideFile(SrcFilePathList, DstPathList):

  #
  # Text Handling
  #
#  RelplaceString(FilePath, BeforStr, AfterStr)
#  InsertStringToFile(FilePath, KeyWord, String)
#  InsertStringToUni(Path, KeyWordStr, TargetStr)
#  DeleteStringFromFile(Path, KeyWord)
#  DeleteStringFromFileEx(FilePath, KeyWord, NumRmLine)
#  ModifyInfFileGuid(FilePath)
#  StringAlign(Path, SampleStr, Format)

if __name__ == "__main__":
  main()

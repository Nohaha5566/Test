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
  # This function will generate a set of GUID
  return uuid.uuid4()

def GetFileList(Regex):
  # This function will get destination file by regular expression
  Buffer = []

  regex = re.compile (Regex)
  for line in os.listdir("."):
    if regex.search(line):
      Buffer.append(str(line))
  return Buffer

def DepthSearchFile(Dst):
  # This function will return dirPath, dirNames, and fileNames
  return os.walk(Dst)

def RenameFile(Src, Dst):
  # This function will rename destination file's name
  return os.rename(Src, Dst)

def CopyFile(Src, Dst):
  # This function will copy source file to destination path
  return shutil.copy2(Src, Dst)

def MoveFile(Src, Dst):
  # This function will move source file to destination path
  return shutil.move(Src, Dst)

def DeleteFile(Dst):
  # This function will delete destination file
  return os.remove(Dst)

def CopyFolder(Src, Dst):
  # This function will copy a source folder to destination path
  return shutil.copytree(Src, Dst)

def DeleteFolder(Dst):
  # This function will delete a destination folder
  return shutil.rmtree(Dst)

def CopyFileContent(Src, Dst):
  # This function will copy source file content to destination file
  return shutil.copyfile(Src, Dst)

def OverrideFile(SrcFilePathList, DstPathList):
  # This function will override file from SrcFilePathList to DstPathList

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
  # This function will replace string from BeforStr to AfterStr
  if os.path.exists(FilePath):
    with fileinput.FileInput(FilePath, inplace=True) as f2:
      for line in f2:
        print(line.replace(BeforStr, AfterStr), end="")

def InsertStringToFile(FilePath, KeyWord, String):
  # This function will insert string under KeyWord string
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

def InsertStringToFileEx(FilePath, KeyWord, SrcFile):
  # This function will insert string under KeyWord string
  Buffer = []
  Src = open(SrcFile, "r")

  with fileinput.FileInput(FilePath, inplace=False) as file2:
     for line in file2:
       if KeyWord in line[0:-1]:
         Buffer.append(line)
         for line2 in Src:
           Buffer.append(line2)
       else:
         Buffer.append(line)

  f = open(FilePath, 'w')
  for line in Buffer:
    f.write(line)
  f.close()

def InsertStringToUni(Path, KeyWord, TargetStr):
  # This function will insert string under KeyWord string(For unicode file)
  Buffer = []

  with codecs.open(Path, encoding='utf-16') as file:
    for line in file:
      if KeyWord in line:
        Buffer.append(line + TargetStr)
      else:
        Buffer.append(line)

  with codecs.open(Path, 'w', encoding='utf-16') as f:
    for line in Buffer:
      f.write(line)

def DeleteStringFromFile(Path, KeyWord):
  # This function will delete string under KeyWord string
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
  # This function will delete multi line string under KeyWord string by NumRmLine(It's a integer number)
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
  # This function will update GUID in a file
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

def ModifyDecAndHeaderFileGuid(FilePath):
  # This function will update GUID in a DEC or Header file
  Buffer = []
  MiddleStr = ""
  regex = re.compile("{.*\w{8}.*\w{4}.*\w{4}.*{.*\w{2}.*\w{2}.*\w{2}.*\w{2}.*\w{2}.*\w{2}.*\w{2}.*\w{2}.*}*}")
  GuidBuffer = []
  count = 0
  with fileinput.FileInput(FilePath, inplace=False) as f:
    for line in f:
      if regex.search(line):
        StartPos = line.find("{")
        EndPos = line.rfind("}")
        list = str(GenerateGuid()).split("-")
        for line2 in list:
          if count >= 3:
            for Index in range(0, len(line2), 2):
               GuidBuffer.append(line2[Index:Index+2])
          else:
            GuidBuffer.append(line2)
          count += 1
        FirstStr = line[0:StartPos]
        print(FirstStr)
        MiddleStr = "{ 0x%s, 0x%s, 0x%s, { 0x%s, 0x%s, 0x%s, 0x%s, 0x%s, 0x%s, 0x%s, 0x%s } }" %(tuple(GuidBuffer))
        LastStr = line[StartPos+len(MiddleStr):-1]
        Buffer.append(FirstStr+MiddleStr+LastStr+"\n")
      else:
        Buffer.append(line)

  TmpFile = open(FilePath, 'w')
  for line in Buffer:
    TmpFile.write(line)
  TmpFile.close()

def StringAlign(Path, SampleStr, Format):
  # This function will make target string align with SampleStr

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
      if regex.search(line) and (len(line.split()) == len(SampleStr.split())):
        Flag = True
        for ArgPos in SplitList:
          Length = len(NewStr)
          NewStr += Space*(ArgPos - Length) + line.split()[Index]
          Index += 1
        Buffer.append(NewStr + "\n")
      elif regex.search(line) and (not (len(line.split()) == len(SampleStr.split()))):
        print("========================== Waring! ==========================")
        print("Sample string size(%d) not equal with KeyWord string size(%d)"  %(len(SampleStr.split()), len(line.split())))
        print("=============================================================")
      else:
        continue

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
#  GetFileList(Regex):
#  DepthSearchFile(Dst):
#  RenameFile(Src, Dst)
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
#  InsertStringToFileEx(FilePath, KeyWord, SrcFile)
#  InsertStringToUni(Path, KeyWordStr, TargetStr)
#  DeleteStringFromFile(Path, KeyWord)
#  DeleteStringFromFileEx(FilePath, KeyWord, NumRmLine)
#  ModifyInfFileGuid(FilePath)
#  ModifyDecAndHeaderFileGuid(FilePath)
#  StringAlign(Path, SampleStr, Format)

if __name__ == "__main__":
  main()

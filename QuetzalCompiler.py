#Analizador sintactico
#Jesus Garcia Hernandez
#Mario Cuevas
#Juan Pablo Hernandez

import sys
import SymbolTable
import colorama
import re
from colorama import Fore

#Imports
skippedCharacters = SymbolTable.skippedCharacters
separators = SymbolTable.separators
reservedWords = SymbolTable.reservedWords
alphabet = SymbolTable.alphabet
characterLiterals = SymbolTable.characterLiterals

#Variables
readedTokens = []  #For lexical analyzing
tokenList = []  #For syntactical analyzing


def readFile():
  global file
  with open(sys.argv[1]) as f:
    file = f.readlines()

# ----------------- Lexical analyze ----------------------------
def lexicalAnalize():
  delimitedComment = False
  stringMode = False

  for line in file:
    currToken = ""
    skipTokens = 0

    for i in range(len(line)):
      if (i + 1 < len(line) and line[i] == '/'
          and line[i + 1] == '/'):  #Skip one line comments
        break
      elif (delimitedComment == False and line[i] == '/'
            and line[i + 1] == '*'):  #Begin of a multiline comment
        delimitedComment = True
      elif (delimitedComment == True and line[i - 1] == '*'
            and line[i] == '/'):  #Ending of a multiline comment
        delimitedComment = False
      elif (delimitedComment == True
            ):  #Skip when analyzer is in multiline comment mode
        continue
      else:
        if (line[i - 1] != '\\' and line[i] == '"' and stringMode == False):
          if (currToken != ""):
            readedTokens.append(currToken)
            currToken = ""
          stringMode = True
          currToken = currToken + line[i]
        elif (line[i - 1] != '\\' and line[i] == '"' and stringMode == True):
          currToken = currToken + line[i]
          readedTokens.append(currToken)
          currToken = ""
          stringMode = False
        elif (stringMode == True):
          currToken = currToken + line[i]
        elif (line[i] in skippedCharacters
              ):  #If there is a skipping token check if currword has something
          if (currToken != ""):
            readedTokens.append(currToken)
            currToken = ""
        elif (skipTokens > 0):  #For multiple character tokens
          skipTokens = skipTokens - 1
        elif (i + 2 < len(line) and line[i] + line[i + 1] + line[i + 2]
              in separators):  # Three character tokens
          if (currToken != ""):
            readedTokens.append(currToken)
            currToken = ""
          readedTokens.append(line[i] + line[i + 1] + line[i + 2])
          skipTokens = 2
        elif (i + 1 < len(line)
              and ((line[i] + line[i + 1] in separators)
                   or line[i] == '\\' and line[i + 1] in characterLiterals)):
          if (currToken != ""):
            readedTokens.append(currToken)
            currToken = ""
          readedTokens.append(line[i] + line[i + 1])
          skipTokens = 1
        #Check this condition
        elif (line[i] in separators):
          if (currToken != ""):
            readedTokens.append(currToken)
            currToken = ""
          readedTokens.append(line[i])
        else:
          currToken = currToken + line[i]

  classifyTokens()

def classifyTokens():

  for i in range(len(readedTokens)):
    if (readedTokens[i] in separators):
      tokenList.append(separators[readedTokens[i]])
      print(readedTokens[i], separators[readedTokens[i]])
    elif (readedTokens[i] in reservedWords):
      tokenList.append(reservedWords[readedTokens[i]])
      print(readedTokens[i], reservedWords[readedTokens[i]])
    else:
      literalValidaton(readedTokens[i])

def literalValidaton(token, secondLap=False):
  if (token[0] == '"' and token[len(token) - 1] == '"'):  #String literal (63)
    tokenList.append(63)
    print(token, 63)
  elif (re.match(r'(^-?[0-9]*$)', token)):  #Numeric literal (64)
    tokenList.append(64)
    print(token, 64)
  elif(token == "false" or token == "true"):  #Boolean literal (65)
    tokenList.append(65)
    print(token, 65)
  elif (token[0] == '\\'):      #Character litral (66)
    if (len(token) > 1):
      if (token[1] in characterLiterals):
        tokenList.append(66)
        print(token, 66)
      elif (re.match(r'(^(\\u)[0-9A-Za-z][0-9A-Za-z][0-9A-Za-z][0-9A-Za-z][0-9A-Za-z][0-9A-Za-z]$)',token)):
        tokenList.append(66)
        print(token, 66)
      else:
        Error(token)
    else:
      tokenList.append(66)
      print(token, 66)
  else:
    tokenValidation(token)

def tokenValidation(token):
  if (token.__contains__('-')):
    currToken = ''
    for i in range(len(token) + 1):
      if (i < len(token) and token[i] == '-' and i != 0):
        literalValidaton(currToken)
        print('-', reservedWords['-'])
        tokenList.append(reservedWords['-'])
        currToken = ''
      elif (i == len(token)):
        literalValidaton(currToken)
        currToken = ''
      else:
        currToken += token[i]
    return

  for character in token:  #Validate each token
    if (character not in alphabet and character not in separators
        and character not in reservedWords):
      Error(token)

  #It is an ID
  tokenList.append(67)
  print(token, 67)


def Error(token):
  print(Fore.RED + "ERROR: Non recognized at line " + searchError(token) +
        Fore.WHITE)
  exit(-1)


def searchError(IncorrectToken):
  for line in range(len(file)):  #Search the error in the code
    if IncorrectToken in file[line]:
      return str(line + 1)

# --------------- Syntactical analyze --------------------------
def syntacticalAnalize():
  ROWS = 144
  TERMINALS = 70
  CONTENT = 2

  actionTable = [[[0 for k in range(CONTENT)] for j in range(TERMINALS)] for i in range(ROWS)]

  gotoTable = [[0] * ROWS] * TERMINALS
  stack = []
  currentToken = None
  nextToken = None
  requested = False
  errorList = []
  lexicalAnalizer = None  #???
  SLRGrammar = None
  compiled = False
  analyzerExit = False
  column = -1
  
  actionTable[0][69][0] = "D"
  actionTable[0][69][1] = "3"

  actionTable[1][68][0] = "acc"
  #-----------------Analysis table----------------------------------------
  #---------------------Mario-----------------------------
  #-----------State 2-----------------
  actionTable[2][48][0] = "D"
  actionTable[2][48][1] = "7"

  actionTable[2][67][0] = "D"
  actionTable[2][67][1] = "8"
  
  actionTable[2][68][0] = "R"
  actionTable[2][68][1] = "1"
  #-----------State 3-----------------
  actionTable[3][48][0] = "R"
  actionTable[3][48][1] = "3"

  actionTable[3][67][0] = "R"
  actionTable[3][67][1] = "3"
  
  actionTable[3][68][0] = "R"
  actionTable[3][68][1] = "3"
  #-----------State 4-----------------
  actionTable[4][48][0] = "R"
  actionTable[4][48][1] = "2"

  actionTable[4][67][0] = "R"
  actionTable[4][67][1] = "2"
  
  actionTable[4][68][0] = "R"
  actionTable[4][68][1] = "2"
  #-----------State 5-----------------
  actionTable[5][48][0] = "R"
  actionTable[5][48][1] = "4"

  actionTable[5][67][0] = "R"
  actionTable[5][67][1] = "4"
  
  actionTable[5][68][0] = "R"
  actionTable[5][68][1] = "4"
  #-----------State 6-----------------
  actionTable[6][48][0] = "R"
  actionTable[6][48][1] = "5"

  actionTable[6][67][0] = "R"
  actionTable[6][67][1] = "5"
  
  actionTable[6][68][0] = "R"
  actionTable[6][68][1] = "5"
  #-----------State 7-----------------
  actionTable[7][67][0] = "D"
  actionTable[7][67][1] = "11"
  #-----------State 8-----------------
  actionTable[8][3][0] = "D"
  actionTable[8][3][1] = "12"
  #-----------State 9-----------------
  actionTable[9][13][0] = "D"
  actionTable[9][13][1] = "13"
  #-----------State 10----------------
  actionTable[10][13][0] = "R"
  actionTable[10][13][1] = "7"
  #-----------State 11----------------
  actionTable[11][69][0] = "D"
  actionTable[11][69][1] = "16"
  
  actionTable[11][2][0] = "D"
  actionTable[11][2][1] = "15"
  #-----------State 12----------------
  actionTable[12][69][0] = "D"
  actionTable[12][69][1] = "19"
  
  actionTable[12][67][0] = "D"
  actionTable[12][67][1] = "11"
    #-----------State 13----------------
  actionTable[13][69][0] = "R"
  actionTable[13][69][1] = "6"

  actionTable[13][48][0] = "R"
  actionTable[13][48][1] = "6"
  
  actionTable[13][67][0] = "R"
  actionTable[13][67][1] = "6"

  actionTable[13][68][0] = "R"
  actionTable[13][68][1] = "6"
  
  #-----------State 14-----------------
  actionTable[14][13][0] = "R"
  actionTable[14][13][1] = "8"

  actionTable[14][4][0] = "R"
  actionTable[14][4][1] = "8"

  #-----------State 15-----------------
  actionTable[15][67][0] = "D"
  actionTable[15][67][1] = "20"

  #-----------State 16-----------------
  actionTable[16][13][0] = "R"
  actionTable[16][13][1] = "10"

  actionTable[16][4][0] = "R"
  actionTable[16][4][1] = "10"

  #-----------State 17-----------------
  actionTable[17][4][0] = "D"
  actionTable[17][4][1] = "21"

  #-----------State 18-----------------
  actionTable[18][4][0] = "R"
  actionTable[18][4][1] = "12"

  #-----------State 19-----------------
  actionTable[19][4][0] = "R"
  actionTable[19][4][1] = "13"

  #-----------State 20-----------------
  actionTable[20][69][0] = "D"
  actionTable[20][69][1] = "16"

  actionTable[20][2][0] = "D"
  actionTable[20][2][1] = "15"

  #-----------State 21-----------------
  actionTable[21][7][0] = "D"
  actionTable[21][7][1] = "23"

  #-----------State 22-----------------
  actionTable[22][13][0] = "R"
  actionTable[22][13][1] = "9"

  actionTable[22][4][0] = "R"
  actionTable[22][4][1] = "9"
  
  #-----------State 23-----------------
  actionTable[23][69][0] = "D"
  actionTable[23][69][1] = "25"

  #-----------State 24-----------------
  actionTable[24][69][0] = "D"
  actionTable[24][69][1] = "28"

  actionTable[24][48][0] = "D"
  actionTable[24][48][1] = "7"

  #-----------State 25-----------------
  actionTable[25][69][0] = "R"
  actionTable[25][69][1] = "15"

  actionTable[25][48][0] = "R"
  actionTable[25][48][1] = "15"

  #-----------State 26-----------------
  actionTable[26][13][0] = "D"
  actionTable[26][13][1] = "48"

  actionTable[26][67][0] = "D"
  actionTable[26][67][1] = "40"

  actionTable[26][8][0] = "D"
  actionTable[26][8][1] = "29"

  actionTable[26][49][0] = "D"
  actionTable[26][49][1] = "41"

  actionTable[26][50][0] = "D"
  actionTable[26][50][1] = "42"

  actionTable[26][51][0] = "D"
  actionTable[26][51][1] = "44"

  actionTable[26][54][0] = "D"
  actionTable[26][54][1] = "45"

  actionTable[26][38][0] = "D"
  actionTable[26][38][1] = "46"

  actionTable[26][57][0] = "D"
  actionTable[26][57][1] = "47"

  #-----------State 27-----------------
  actionTable[27][69][0] = "R"
  actionTable[27][69][1] = "14"

  actionTable[27][48][0] = "R"
  actionTable[27][48][1] = "14"

  #-----------State 28-----------------
  actionTable[28][13][0] = "R"
  actionTable[28][13][1] = "17"

  actionTable[28][67][0] = "R"
  actionTable[28][67][1] = "17"

  actionTable[28][8][0] = "R"
  actionTable[26][8][1] = "17"

  actionTable[28][49][0] = "R"
  actionTable[28][49][1] = "17"

  actionTable[28][50][0] = "R"
  actionTable[28][50][1] = "17"

  actionTable[28][51][0] = "R"
  actionTable[28][51][1] = "17"

  actionTable[28][54][0] = "R"
  actionTable[28][54][1] = "17"

  actionTable[28][38][0] = "R"
  actionTable[28][38][1] = "17"

  actionTable[28][57][0] = "R"
  actionTable[28][57][1] = "17"

  #-----------State 29----------------
  actionTable[29][48][0] = "R"
  actionTable[29][48][1] = "11"
  
  actionTable[29][67][0] = "R"
  actionTable[29][67][1] = "11"

  actionTable[20][68][0] = "R"
  actionTable[29][68][1] = "11"

  #-----------State 30-----------------
  actionTable[30][13][0] = "R"
  actionTable[30][13][1] = "16"

  actionTable[30][67][0] = "R"
  actionTable[30][67][1] = "16"

  actionTable[30][8][0] = "R"
  actionTable[30][8][1] = "16"

  actionTable[30][49][0] = "R"
  actionTable[30][49][1] = "16"

  actionTable[30][50][0] = "R"
  actionTable[30][50][1] = "16"

  actionTable[30][51][0] = "R"
  actionTable[30][51][1] = "16"

  actionTable[30][54][0] = "R"
  actionTable[30][54][1] = "16"

  actionTable[30][38][0] = "R"
  actionTable[30][38][1] = "16"

  actionTable[30][57][0] = "R"
  actionTable[30][57][1] = "16"

    #-----------State 31-----------------
  actionTable[31][13][0] = "R"
  actionTable[31][13][1] = "18"

  actionTable[31][67][0] = "R"
  actionTable[31][67][1] = "18"

  actionTable[31][8][0] = "R"
  actionTable[31][8][1] = "18"

  actionTable[31][49][0] = "R"
  actionTable[31][49][1] = "18"

  actionTable[31][50][0] = "R"
  actionTable[31][50][1] = "18"

  actionTable[31][51][0] = "R"
  actionTable[31][51][1] = "18"

  actionTable[31][54][0] = "R"
  actionTable[31][54][1] = "18"

  actionTable[31][38][0] = "R"
  actionTable[31][38][1] = "18"

  actionTable[31][57][0] = "R"
  actionTable[31][57][1] = "18"

  #-----------State 32-----------------
  actionTable[32][13][0] = "R"
  actionTable[32][13][1] = "19"

  actionTable[32][67][0] = "R"
  actionTable[32][67][1] = "19"

  actionTable[32][8][0] = "R"
  actionTable[32][8][1] = "19"

  actionTable[32][49][0] = "R"
  actionTable[32][49][1] = "19"

  actionTable[32][50][0] = "R"
  actionTable[32][50][1] = "19"

  actionTable[32][51][0] = "R"
  actionTable[32][51][1] = "19"

  actionTable[32][54][0] = "R"
  actionTable[32][54][1] = "19"

  actionTable[32][38][0] = "R"
  actionTable[32][38][1] = "19"

  actionTable[32][57][0] = "R"
  actionTable[32][57][1] = "19"

  #-----------State 33-----------------
  actionTable[33][13][0] = "R"
  actionTable[33][13][1] = "20"

  actionTable[33][67][0] = "R"
  actionTable[33][67][1] = "20"

  actionTable[33][8][0] = "R"
  actionTable[33][8][1] = "20"

  actionTable[33][49][0] = "R"
  actionTable[33][49][1] = "20"

  actionTable[33][50][0] = "R"
  actionTable[33][50][1] = "20"

  actionTable[33][51][0] = "R"
  actionTable[33][51][1] = "20"

  actionTable[33][54][0] = "R"
  actionTable[33][54][1] = "20"

  actionTable[33][38][0] = "R"
  actionTable[33][38][1] = "20"

  actionTable[33][57][0] = "R"
  actionTable[33][57][1] = "20"  

  #-----------State 34-----------------
  actionTable[34][13][0] = "R"
  actionTable[34][13][1] = "21"

  actionTable[34][67][0] = "R"
  actionTable[34][67][1] = "21"

  actionTable[34][8][0] = "R"
  actionTable[34][8][1] = "21"

  actionTable[34][49][0] = "R"
  actionTable[34][49][1] = "21"

  actionTable[34][50][0] = "R"
  actionTable[34][50][1] = "21"

  actionTable[34][51][0] = "R"
  actionTable[34][51][1] = "21"

  actionTable[34][54][0] = "R"
  actionTable[34][54][1] = "21"

  actionTable[34][38][0] = "R"
  actionTable[34][38][1] = "21"

  actionTable[34][57][0] = "R"
  actionTable[34][57][1] = "21"  

  #-----------State 35-----------------
  actionTable[35][13][0] = "R"
  actionTable[35][13][1] = "22"

  actionTable[35][67][0] = "R"
  actionTable[35][67][1] = "22"

  actionTable[35][8][0] = "R"
  actionTable[35][8][1] = "22"

  actionTable[35][49][0] = "R"
  actionTable[35][49][1] = "22"

  actionTable[35][50][0] = "R"
  actionTable[35][50][1] = "22"

  actionTable[35][51][0] = "R"
  actionTable[35][51][1] = "22"

  actionTable[35][54][0] = "R"
  actionTable[35][54][1] = "22"

  actionTable[35][38][0] = "R"
  actionTable[35][38][1] = "22"

  actionTable[35][57][0] = "R"
  actionTable[35][57][1] = "22" 

    #-----------State 36-----------------
  actionTable[36][13][0] = "R"
  actionTable[36][13][1] = "23"

  actionTable[36][67][0] = "R"
  actionTable[36][67][1] = "23"

  actionTable[36][8][0] = "R"
  actionTable[36][8][1] = "23"

  actionTable[36][49][0] = "R"
  actionTable[36][49][1] = "23"

  actionTable[36][50][0] = "R"
  actionTable[36][50][1] = "23"

  actionTable[36][51][0] = "R"
  actionTable[36][51][1] = "23"

  actionTable[36][54][0] = "R"
  actionTable[36][54][1] = "23"

  actionTable[36][38][0] = "R"
  actionTable[36][38][1] = "23"

  actionTable[36][57][0] = "R"
  actionTable[36][57][1] = "23" 

  #-----------State 37-----------------
  actionTable[37][13][0] = "R"
  actionTable[37][13][1] = "24"

  actionTable[37][67][0] = "R"
  actionTable[37][67][1] = "24"

  actionTable[37][8][0] = "R"
  actionTable[37][8][1] = "24"

  actionTable[37][49][0] = "R"
  actionTable[37][49][1] = "24"

  actionTable[37][50][0] = "R"
  actionTable[37][50][1] = "24"

  actionTable[37][51][0] = "R"
  actionTable[37][51][1] = "24"

  actionTable[37][54][0] = "R"
  actionTable[37][54][1] = "24"

  actionTable[37][38][0] = "R"
  actionTable[37][38][1] = "24"

  actionTable[37][57][0] = "R"
  actionTable[37][57][1] = "24" 

    #-----------State 38-----------------
  actionTable[38][13][0] = "R"
  actionTable[38][13][1] = "25"

  actionTable[38][67][0] = "R"
  actionTable[38][67][1] = "25"

  actionTable[38][8][0] = "R"
  actionTable[38][8][1] = "25"

  actionTable[38][49][0] = "R"
  actionTable[38][49][1] = "25"

  actionTable[38][50][0] = "R"
  actionTable[38][50][1] = "25"

  actionTable[38][51][0] = "R"
  actionTable[38][51][1] = "25"

  actionTable[38][54][0] = "R"
  actionTable[38][54][1] = "25"

  actionTable[38][38][0] = "R"
  actionTable[38][38][1] = "25"

  actionTable[38][57][0] = "R"
  actionTable[38][57][1] = "25" 

  #-----------State 39-----------------
  actionTable[39][13][0] = "R"
  actionTable[39][13][1] = "26"

  actionTable[39][67][0] = "R"
  actionTable[39][67][1] = "26"

  actionTable[39][8][0] = "R"
  actionTable[39][8][1] = "26"

  actionTable[39][49][0] = "R"
  actionTable[39][49][1] = "26"

  actionTable[39][50][0] = "R"
  actionTable[39][50][1] = "26"

  actionTable[39][51][0] = "R"
  actionTable[39][51][1] = "26"

  actionTable[39][54][0] = "R"
  actionTable[39][54][1] = "26"

  actionTable[39][38][0] = "R"
  actionTable[39][38][1] = "26"

  actionTable[39][57][0] = "R"
  actionTable[39][57][1] = "26" 

  #-----------State 40-----------------
  actionTable[40][3][0] = "D"
  actionTable[40][3][1] = "50"

  actionTable[40][14][0] = "D"
  actionTable[40][14][1] = "49"

  #-----------State 41-----------------
  actionTable[41][67][0] = "D"
  actionTable[41][67][1] = "51"

  #-----------State 42-----------------
  actionTable[42][67][0] = "D"
  actionTable[42][67][1] = "52"

  #-----------State 43-----------------
  actionTable[43][13][0] = "D"
  actionTable[43][13][1] = "53"
  
  #-----------State 44-----------------
  actionTable[44][3][0] = "D"
  actionTable[44][3][1] = "54"

  #-----------State 45-----------------
  actionTable[45][7][0] = "D"
  actionTable[45][7][1] = "55"

  #-----------State 46-----------------
  actionTable[46][13][0] = "D"
  actionTable[46][13][1] = "56"

  #-----------State 46-----------------
  actionTable[46][13][0] = "D"
  actionTable[46][13][1] = "56"

  #-----------State 47-----------------
  actionTable[47][67][0] = "D"
  actionTable[47][67][1] = "70"

  actionTable[47][3][0] = "D"
  actionTable[47][3][1] = "74"

  actionTable[47][1][0] = "D"
  actionTable[47][1][1] = "67"

  actionTable[47][39][0] = "D"
  actionTable[47][39][1] = "68"

  actionTable[47][61][0] = "D"
  actionTable[47][61][1] = "69"

  actionTable[47][5][0] = "D"
  actionTable[47][5][1] = "75"

  actionTable[47][65][0] = "D"
  actionTable[47][65][1] = "76"

  actionTable[47][64][0] = "D"
  actionTable[47][64][1] = "77"

  actionTable[47][66][0] = "D"
  actionTable[47][66][1] = "78" 

  actionTable[47][63][0] = "D"
  actionTable[47][63][1] = "79" 

    #-----------State 48-----------------
  actionTable[48][13][0] = "R"
  actionTable[48][13][1] = "44"

  actionTable[48][67][0] = "R"
  actionTable[48][67][1] = "44"

  actionTable[48][7][0] = "R"
  actionTable[48][7][1] = "44"

  actionTable[48][49][0] = "R"
  actionTable[48][49][1] = "44"

  actionTable[48][50][0] = "R"
  actionTable[48][50][1] = "44"

  actionTable[48][51][0] = "R"
  actionTable[48][51][1] = "44"

  actionTable[48][54][0] = "R"
  actionTable[48][54][1] = "44"

  actionTable[48][38][0] = "R"
  actionTable[48][38][1] = "44"

  actionTable[48][57][0] = "R"
  actionTable[48][57][1] = "44" 

  #-----------State 49-----------------
  actionTable[49][67][0] = "D"
  actionTable[49][67][1] = "70"

  actionTable[49][3][0] = "D"
  actionTable[49][3][1] = "74"

  actionTable[49][1][0] = "D"
  actionTable[49][1][1] = "67"

  actionTable[49][39][0] = "D"
  actionTable[49][39][1] = "68"

  actionTable[49][61][0] = "D"
  actionTable[49][61][1] = "69"

  actionTable[49][5][0] = "D"
  actionTable[49][5][1] = "75"

  actionTable[49][65][0] = "D"
  actionTable[49][65][1] = "76"

  actionTable[49][64][0] = "D"
  actionTable[49][64][1] = "77"

  actionTable[49][66][0] = "D"
  actionTable[49][66][1] = "78" 

  actionTable[49][63][0] = "D"
  actionTable[49][63][1] = "79" 

  #-----------State 50-----------------
  actionTable[50][69][0] = "D"
  actionTable[50][69][1] = "83"
  
  actionTable[50][67][0] = "D"
  actionTable[50][67][1] = "70"

  actionTable[50][3][0] = "D"
  actionTable[50][3][1] = "74"

  actionTable[50][1][0] = "D"
  actionTable[50][1][1] = "67"

  actionTable[50][39][0] = "D"
  actionTable[50][39][1] = "68"

  actionTable[50][61][0] = "D"
  actionTable[50][61][1] = "69"

  actionTable[50][5][0] = "D"
  actionTable[50][5][1] = "75"

  actionTable[50][65][0] = "D"
  actionTable[50][65][1] = "76"

  actionTable[50][64][0] = "D"
  actionTable[50][64][1] = "77"

  actionTable[50][66][0] = "D"
  actionTable[50][66][1] = "78" 

  actionTable[50][63][0] = "D"
  actionTable[50][63][1] = "79" 

  #---------------------Juanpa-----------------------------
  #actionTable[estado][numero del terminal][caracterEnLaCadena]
  #-----------State 66-----------------
  actionTable[66][69][0]= "R"
  actionTable[66][69][0]= "70"
  
  actionTable[66][13][0]="R"
  actionTable[66][13][1]="70"

  actionTable[66][2][0]="R"
  actionTable[66][2][1]="70"

  actionTable[66][4][0]="R"
  actionTable[66][4][1]="70"

  actionTable[66][41][0]="R"
  actionTable[66][41][1]="70"
  
  actionTable[66][40][0]="R"
  actionTable[66][40][1]="70"
  
  actionTable[66][25][0]="R"
  actionTable[66][25][1]="70"

  actionTable[66][24][0]="R"
  actionTable[66][24][1]="70"

  actionTable[66][20][0]="R"
  actionTable[66][20][1]="70"

  actionTable[66][22][0]="R"
  actionTable[66][22][1]="70"

  actionTable[66][21][0]="R"
  actionTable[66][21][1]="70"

  actionTable[66][23][0]="R"
  actionTable[66][23][1]="70"

  actionTable[66][1][0]="R"
  actionTable[66][1][1]="70"

  actionTable[66][39][0]="R"
  actionTable[66][39][1]="70"

  actionTable[66][9][0]="R"
  actionTable[66][9][1]="70"

  actionTable[66][11][0]="R"
  actionTable[66][11][1]="70"

  actionTable[66][10][0]="R"
  actionTable[66][10][1]="70"
  #-----------State 67-----------------
  actionTable[67][67][0]="R"
  actionTable[67][67][1]="71"

  actionTable[67][3][0]="R"
  actionTable[67][3][1]="71"

  actionTable[67][1][0]="R"
  actionTable[67][1][1]="71"

  actionTable[67][39][0]="R"
  actionTable[67][39][1]="71"

  actionTable[67][61][0]="R"
  actionTable[67][61][1]="71"

  actionTable[67][5][0]="R"
  actionTable[67][5][1]="71"

  actionTable[67][65][0]="R"
  actionTable[67][65][1]="71"

  actionTable[67][64][0]="R"
  actionTable[67][64][1]="71"

  actionTable[67][66][0]="R"
  actionTable[67][66][1]="71"

  actionTable[67][63][0]="R"
  actionTable[67][63][1]="71"
  
  #-----------State 68-----------------
  actionTable[68][67][0]="R"
  actionTable[68][67][1]="72"

  actionTable[68][3][0]="R"
  actionTable[68][3][1]="72"

  actionTable[68][1][0]="R"
  actionTable[68][1][1]="72"
  
  actionTable[68][39][0]="R"
  actionTable[68][39][1]="72"

  actionTable[68][61][0]="R"
  actionTable[68][61][1]="72"

  actionTable[68][5][0]="R"
  actionTable[68][5][1]="72"

  actionTable[68][65][0]="R"
  actionTable[68][65][1]="72"

  actionTable[68][64][0]="R"
  actionTable[68][64][1]="72"

  actionTable[68][66][0]="R"
  actionTable[68][66][1]="72"

  actionTable[68][63][0]="R"
  actionTable[68][63][1]="72"
  
  #-----------State 69-----------------
  actionTable[69][67][0]="R"
  actionTable[69][67][1]="73"

  actionTable[69][3][0]="R"
  actionTable[69][3][1]="73"

  actionTable[69][1][0]="R"
  actionTable[69][1][1]="73"

  actionTable[69][39][0]="R"
  actionTable[69][39][1]="73"

  actionTable[69][61][0]="R"
  actionTable[69][61][1]="73"

  actionTable[69][5][0]="R"
  actionTable[69][5][1]="73"

  actionTable[69][65][0]="R"
  actionTable[69][65][1]="73"

  actionTable[69][64][0]="R"
  actionTable[69][64][1]="73"

  actionTable[69][66][0]="R"
  actionTable[69][66][1]="73"

  actionTable[69][63][0]="R"
  actionTable[69][63][1]="73"

  #-----------State 70-----------------
  actionTable[70][69][0]="R"
  actionTable[70][69][1]="74"

  actionTable[70][13][0]="R"
  actionTable[70][13][1]="74"

  actionTable[70][2][0]="R"
  actionTable[70][2][1]="74"

  actionTable[70][3][0]="D"
  actionTable[70][3][1]="50"
  
  actionTable[70][4][0]="R"
  actionTable[70][4][1]="74"

  actionTable[70][41][0]="R"
  actionTable[70][41][1]="74"

  actionTable[70][40][0]="R"
  actionTable[70][40][1]="74"

  actionTable[70][25][0]="R"
  actionTable[70][25][1]="74"

  actionTable[70][24][0]="R"
  actionTable[70][24][1]="74"
  
  actionTable[70][20][0]="R"
  actionTable[70][20][1]="74"

  actionTable[70][22][0]="R"
  actionTable[70][22][1]="74"

  actionTable[70][21][0]="R"
  actionTable[70][21][1]="74"

  actionTable[70][23][0]="R"
  actionTable[70][23][1]="74"

  actionTable[70][1][0]="R"
  actionTable[70][1][1]="74"

  actionTable[70][39][0]="R"
  actionTable[70][39][1]="74"

  actionTable[70][9][0]="R"
  actionTable[70][9][1]="74"

  actionTable[70][11][0]="R"
  actionTable[70][11][1]="74"

  actionTable[70][10][0]="R"
  actionTable[70][10][1]="74"

  #-----------State 71-----------------
  actionTable[71][69][0]="R"
  actionTable[71][69][1]="75"

  actionTable[71][13][0]="R"
  actionTable[71][13][1]="75"

  actionTable[71][2][0]="R"
  actionTable[71][2][1]="75"
  
  actionTable[71][4][0]="R"
  actionTable[71][4][1]="75"

  actionTable[71][41][0]="R"
  actionTable[71][41][1]="75"

  actionTable[71][40][0]="R"
  actionTable[71][40][1]="75"

  actionTable[71][25][0]="R"
  actionTable[71][25][1]="75"

  actionTable[71][24][0]="R"
  actionTable[71][24][1]="75"
  
  actionTable[71][20][0]="R"
  actionTable[71][20][1]="75"

  actionTable[71][22][0]="R"
  actionTable[71][22][1]="75"

  actionTable[71][21][0]="R"
  actionTable[71][21][1]="74"

  actionTable[71][23][0]="R"
  actionTable[71][23][1]="75"

  actionTable[71][1][0]="R"
  actionTable[71][1][1]="75"

  actionTable[71][39][0]="R"
  actionTable[71][39][1]="75"

  actionTable[71][9][0]="R"
  actionTable[71][9][1]="75"

  actionTable[71][11][0]="R"
  actionTable[71][11][1]="75"

  actionTable[71][10][0]="R"
  actionTable[71][10][1]="75"

  #-----------State 72-----------------
  actionTable[72][69][0]="R"
  actionTable[72][69][1]="76"

  actionTable[72][13][0]="R"
  actionTable[72][13][1]="76"

  actionTable[72][2][0]="R"
  actionTable[72][2][1]="76"
  
  actionTable[72][4][0]="R"
  actionTable[72][4][1]="76"

  actionTable[72][41][0]="R"
  actionTable[72][41][1]="76"

  actionTable[72][40][0]="R"
  actionTable[72][40][1]="76"

  actionTable[72][25][0]="R"
  actionTable[72][25][1]="76"

  actionTable[72][24][0]="R"
  actionTable[72][24][1]="76"
  
  actionTable[72][20][0]="R"
  actionTable[72][20][1]="76"

  actionTable[72][22][0]="R"
  actionTable[72][22][1]="76"

  actionTable[72][21][0]="R"
  actionTable[72][21][1]="76"

  actionTable[72][23][0]="R"
  actionTable[72][23][1]="76"

  actionTable[72][1][0]="R"
  actionTable[72][1][1]="76"

  actionTable[72][39][0]="R"
  actionTable[72][39][1]="76"

  actionTable[72][9][0]="R"
  actionTable[72][9][1]="76"

  actionTable[72][11][0]="R"
  actionTable[72][11][1]="76"

  actionTable[72][10][0]="R"
  actionTable[72][10][1]="76"

  #-----------State 73-----------------
  actionTable[73][69][0]="R"
  actionTable[73][69][1]="77"

  actionTable[73][13][0]="R"
  actionTable[73][13][1]="77"

  actionTable[73][2][0]="R"
  actionTable[73][2][1]="77"
  
  actionTable[73][4][0]="R"
  actionTable[73][4][1]="77"

  actionTable[73][41][0]="R"
  actionTable[73][41][1]="77"

  actionTable[73][40][0]="R"
  actionTable[73][40][1]="77"

  actionTable[73][25][0]="R"
  actionTable[73][25][1]="77"

  actionTable[73][24][0]="R"
  actionTable[73][24][1]="77"
  
  actionTable[73][20][0]="R"
  actionTable[73][20][1]="77"

  actionTable[73][22][0]="R"
  actionTable[73][22][1]="77"

  actionTable[73][21][0]="R"
  actionTable[73][21][1]="77"

  actionTable[73][23][0]="R"
  actionTable[73][23][1]="77"

  actionTable[73][1][0]="R"
  actionTable[73][1][1]="77"

  actionTable[73][39][0]="R"
  actionTable[73][39][1]="77"

  actionTable[73][9][0]="R"
  actionTable[73][9][1]="77"

  actionTable[73][11][0]="R"
  actionTable[73][11][1]="77"

  actionTable[73][10][0]="R"
  actionTable[73][10][1]="77"

  #-----------State 74-----------------
  actionTable[74][67][0]="D"
  actionTable[74][67][1]="70"

  actionTable[74][3][0]="D"
  actionTable[74][3][1]="74"

  actionTable[74][1][0]="D"
  actionTable[74][1][1]="67"

  actionTable[74][39][0]="D"
  actionTable[74][39][1]="68"

  actionTable[74][61][0]="D"
  actionTable[74][61][1]="69"

  actionTable[74][5][0]="D"
  actionTable[74][5][1]="75"

  actionTable[74][65][0]="D"
  actionTable[74][65][1]="76"

  actionTable[74][64][0]="D"
  actionTable[74][64][1]="77"

  actionTable[74][66][0]="D"
  actionTable[74][66][1]="78"

  actionTable[74][63][0]="D"
  actionTable[74][63][1]="79"

  #-----------State 75-----------------
  actionTable[75][69][0]="D"
  actionTable[75][69][1]="83"

  actionTable[75][67][0]="D"
  actionTable[75][67][1]="70"

  actionTable[75][3][0]="D"
  actionTable[75][3][1]="74"

  actionTable[75][1][0]="D"
  actionTable[75][1][1]="67"

  actionTable[75][39][0]="D"
  actionTable[75][39][1]="68"

  actionTable[75][61][0]="D"
  actionTable[75][61][1]="69"

  actionTable[75][5][0]="D"
  actionTable[75][5][1]="75"

  actionTable[75][65][0]="D"
  actionTable[75][65][1]="76"

  actionTable[75][64][0]="D"
  actionTable[75][64][1]="77"

  actionTable[75][66][0]="D"
  actionTable[75][66][1]="78"

  actionTable[75][63][0]="D"
  actionTable[75][63][1]="79"

  #-----------State 76-----------------
  actionTable[76][69][0]="R"
  actionTable[76][69][1]="80"

  actionTable[76][13][0]="R"
  actionTable[76][13][1]="80"

  actionTable[76][2][0]="R"
  actionTable[76][2][1]="80"

  actionTable[76][4][0]="R"
  actionTable[76][4][1]="80"

  actionTable[76][41][0]="R"
  actionTable[76][41][1]="80"

  actionTable[76][40][0]="R"
  actionTable[76][40][1]="80"

  actionTable[76][25][0]="R"
  actionTable[76][25][1]="80"

  actionTable[76][24][0]="R"
  actionTable[76][24][1]="80"

  actionTable[76][20][0]="R"
  actionTable[76][20][1]="80"

  actionTable[76][22][0]="R"
  actionTable[76][22][1]="80"

  actionTable[76][21][0]="R"
  actionTable[76][21][1]="80"

  actionTable[76][23][0]="R"
  actionTable[76][23][1]="80"

  actionTable[76][1][0]="R"
  actionTable[76][1][1]="80"

  actionTable[76][39][0]="R"
  actionTable[76][39][1]="80"

  actionTable[76][9][0]="R"
  actionTable[76][9][1]="80"

  actionTable[76][11][0]="R"
  actionTable[76][11][1]="80"

  actionTable[76][10][0]="R"
  actionTable[76][10][1]="80"

  #-----------State 77-----------------
  actionTable[77][69][0]="R"
  actionTable[77][69][1]="81"

  actionTable[77][13][0]="R"
  actionTable[77][13][1]="81"

  actionTable[77][2][0]="R"
  actionTable[77][2][1]="81"

  actionTable[77][4][0]="R"
  actionTable[77][4][1]="81"

  actionTable[77][41][0]="R"
  actionTable[77][41][1]="81"

  actionTable[77][40][0]="R"
  actionTable[77][40][1]="81"

  actionTable[77][25][0]="R"
  actionTable[77][25][1]="81"

  actionTable[77][24][0]="R"
  actionTable[77][24][1]="81"

  actionTable[77][20][0]="R"
  actionTable[77][20][1]="81"

  actionTable[77][22][0]="R"
  actionTable[77][22][1]="81"

  actionTable[77][21][0]="R"
  actionTable[77][21][1]="81"

  actionTable[77][23][0]="R"
  actionTable[77][23][1]="81"

  actionTable[77][1][0]="R"
  actionTable[77][1][1]="81"

  actionTable[77][39][0]="R"
  actionTable[77][39][1]="81"

  actionTable[77][9][0]="R"
  actionTable[77][9][1]="81"

  actionTable[77][11][0]="R"
  actionTable[77][11][1]="81"

  actionTable[77][10][0]="R"
  actionTable[77][10][1]="81"
  
  #-----------State 78-----------------
  actionTable[78][69][0]="R"
  actionTable[78][69][1]="82"

  actionTable[78][13][0]="R"
  actionTable[78][13][1]="82"

  actionTable[78][2][0]="R"
  actionTable[78][2][1]="82"

  actionTable[78][4][0]="R"
  actionTable[78][4][1]="82"

  actionTable[78][41][0]="R"
  actionTable[78][41][1]="82"

  actionTable[78][40][0]="R"
  actionTable[78][40][1]="82"

  actionTable[78][25][0]="R"
  actionTable[78][25][1]="82"

  actionTable[78][24][0]="R"
  actionTable[78][24][1]="82"

  actionTable[78][20][0]="R"
  actionTable[78][20][1]="82"

  actionTable[78][22][0]="R"
  actionTable[78][22][1]="82"

  actionTable[78][21][0]="R"
  actionTable[78][21][1]="82"

  actionTable[78][23][0]="R"
  actionTable[78][23][1]="82"

  actionTable[78][1][0]="R"
  actionTable[78][1][1]="82"

  actionTable[78][39][0]="R"
  actionTable[78][39][1]="82"

  actionTable[78][9][0]="R"
  actionTable[78][9][1]="82"

  actionTable[78][11][0]="R"
  actionTable[78][11][1]="82"

  actionTable[78][10][0]="R"
  actionTable[78][10][1]="82"
  
  #-----------State 79-----------------
  actionTable[79][69][0]="R"
  actionTable[79][69][1]="83"

  actionTable[79][13][0]="R"
  actionTable[79][13][1]="83"

  actionTable[79][2][0]="R"
  actionTable[79][2][1]="83"

  actionTable[79][4][0]="R"
  actionTable[79][4][1]="83"

  actionTable[79][41][0]="R"
  actionTable[79][41][1]="83"

  actionTable[79][40][0]="R"
  actionTable[79][40][1]="83"

  actionTable[79][25][0]="R"
  actionTable[79][25][1]="83"

  actionTable[79][24][0]="R"
  actionTable[79][24][1]="83"

  actionTable[79][20][0]="R"
  actionTable[79][20][1]="83"

  actionTable[79][22][0]="R"
  actionTable[79][22][1]="83"

  actionTable[79][21][0]="R"
  actionTable[79][21][1]="83"

  actionTable[79][23][0]="R"
  actionTable[79][23][1]="83"

  actionTable[79][1][0]="R"
  actionTable[79][1][1]="83"

  actionTable[79][39][0]="R"
  actionTable[79][39][1]="83"

  actionTable[79][9][0]="R"
  actionTable[79][9][1]="83"

  actionTable[79][11][0]="R"
  actionTable[79][11][1]="83"

  actionTable[79][10][0]="R"
  actionTable[79][10][1]="83"
  
  #-----------State 80-----------------
  actionTable[80][13][0]="D"
  actionTable[80][13][1]="109"
  
  #-----------State 81-----------------
  actionTable[81][4][0]="D"
  actionTable[81][4][1]="110"
  
  #-----------State 82-----------------
  actionTable[82][69][0]="D"
  actionTable[82][69][1]="113"

  actionTable[82][2][0]="D"
  actionTable[82][2][1]="112"
  
  #-----------State 83-----------------
  actionTable[83][4][0]="R"
  actionTable[83][4][1]="33"

  actionTable[83][6][0]="R"
  actionTable[83][6][1]="33"
  
  #-----------State 84-----------------
  actionTable[84][13][0]="R"
  actionTable[84][13][1]="28"

  actionTable[84][67][0]="R"
  actionTable[84][67][1]="28"

  actionTable[84][8][0]="R"
  actionTable[84][8][1]="28"

  actionTable[84][49][0]="R"
  actionTable[84][49][1]="28"

  actionTable[84][50][0]="R"
  actionTable[84][50][1]="28"

  actionTable[84][51][0]="R"
  actionTable[84][51][1]="28"

  actionTable[84][54][0]="R"
  actionTable[84][54][1]="28"

  actionTable[84][38][0]="R"
  actionTable[84][38][1]="28"

  actionTable[84][57][0]="R"
  actionTable[84][57][1]="28"
  
  #-----------State 85-----------------
  actionTable[85][13][0]="R"
  actionTable[85][13][1]="29"
  
  actionTable[85][67][0]="R"
  actionTable[85][67][1]="29"

  actionTable[85][8][0]="R"
  actionTable[85][8][1]="29"

  actionTable[85][49][0]="R"
  actionTable[85][49][1]="29"

  actionTable[85][50][0]="R"
  actionTable[85][50][1]="29"

  actionTable[85][51][0]="R"
  actionTable[85][51][1]="29"

  actionTable[85][54][0]="R"
  actionTable[85][54][1]="29"

  actionTable[85][38][0]="R"
  actionTable[85][38][1]="29"

  actionTable[85][57][0]="R"
  actionTable[85][57][1]="29"

  #-----------State 86-----------------
  actionTable[86][4][0]="D"
  actionTable[86][4][1]="144"
  
  #-----------State 87-----------------
  actionTable[87][13][0]="D"
  actionTable[87][13][1]="48"

  actionTable[87][67][0]="D"
  actionTable[87][67][1]="40"

  actionTable[87][8][0]="D"
  actionTable[87][8][1]="115"

  actionTable[87][49][0]="D"
  actionTable[87][49][1]="41"

  actionTable[87][50][0]="D"
  actionTable[87][50][1]="42"

  actionTable[87][51][0]="D"
  actionTable[87][51][1]="44"

  actionTable[87][54][0]="D"
  actionTable[87][54][1]="45"

  actionTable[87][38][0]="D"
  actionTable[87][38][1]="46"

  actionTable[87][57][0]="D"
  actionTable[87][57][1]="47"

  #-----------State 88-----------------
  actionTable[88][13][0]="R"
  actionTable[88][13][1]="43"

  actionTable[88][67][0]="R"
  actionTable[88][67][1]="43"

  actionTable[88][8][0]="R"
  actionTable[88][8][1]="43"

  actionTable[88][49][0]="R"
  actionTable[88][49][1]="43"

  actionTable[88][50][0]="R"
  actionTable[88][50][1]="43"

  actionTable[88][51][0]="R"
  actionTable[88][51][1]="43"

  actionTable[88][54][0]="R"
  actionTable[88][54][1]="43"

  actionTable[88][38][0]="R"
  actionTable[88][38][1]="43"

  actionTable[88][57][0]="R"
  actionTable[88][57][1]="43"
  
  #-----------State 89-----------------
  actionTable[89][67][0]="D"
  actionTable[89][67][1]="70"

  actionTable[89][3][0]="D"
  actionTable[89][3][1]="74"

  actionTable[89][1][0]="D"
  actionTable[89][1][1]="67"

  actionTable[89][39][0]="D"
  actionTable[89][39][1]="68"

  actionTable[89][61][0]="D"
  actionTable[89][61][1]="69"

  actionTable[89][5][0]="D"
  actionTable[89][5][1]="75"

  actionTable[89][65][0]="D"
  actionTable[89][65][1]="76"

  actionTable[89][64][0]="D"
  actionTable[89][64][1]="77"

  actionTable[89][66][0]="D"
  actionTable[89][66][1]="78"

  actionTable[89][63][0]="D"
  actionTable[89][63][1]="79"
  
  #-----------State 90-----------------
  actionTable[90][67][0]="D"
  actionTable[90][67][1]="70"

  actionTable[90][3][0]="D"
  actionTable[90][3][1]="74"

  actionTable[90][1][0]="D"
  actionTable[90][1][1]="67"

  actionTable[90][39][0]="D"
  actionTable[90][39][1]="68"

  actionTable[90][61][0]="D"
  actionTable[90][61][1]="69"

  actionTable[90][5][0]="D"
  actionTable[90][5][1]="75"

  actionTable[90][65][0]="D"
  actionTable[90][65][1]="76"

  actionTable[90][64][0]="D"
  actionTable[90][64][1]="77"

  actionTable[90][66][0]="D"
  actionTable[90][66][1]="78"

  actionTable[90][63][0]="D"
  actionTable[90][63][1]="79"
  
  #-----------State 91-----------------
  actionTable[91][67][0]="D"
  actionTable[91][67][1]="70"

  actionTable[91][3][0]="D"
  actionTable[91][3][1]="74"

  actionTable[91][1][0]="D"
  actionTable[91][1][1]="67"

  actionTable[91][39][0]="D"
  actionTable[91][39][1]="68"

  actionTable[91][61][0]="D"
  actionTable[91][61][1]="69"

  actionTable[91][5][0]="D"
  actionTable[91][5][1]="75"

  actionTable[91][65][0]="D"
  actionTable[91][65][1]="76"

  actionTable[91][64][0]="D"
  actionTable[91][64][1]="77"

  actionTable[91][66][0]="D"
  actionTable[91][66][1]="78"

  actionTable[91][63][0]="D"
  actionTable[91][63][1]="79"
  
  #-----------State 92-----------------
  actionTable[92][67][0]="R"
  actionTable[92][67][1]="52"

  actionTable[92][3][0]="R"
  actionTable[92][3][1]="52"

  actionTable[92][1][0]="R"
  actionTable[92][1][1]="52"

  actionTable[92][39][0]="R"
  actionTable[92][39][1]="52"

  actionTable[92][61][0]="R"
  actionTable[92][61][1]="52"

  actionTable[92][5][0]="R"
  actionTable[92][5][1]="52"

  actionTable[92][65][0]="R"
  actionTable[92][65][1]="52"

  actionTable[92][64][0]="R"
  actionTable[92][64][1]="52"

  actionTable[92][66][0]="R"
  actionTable[92][66][1]="52"

  actionTable[92][63][0]="R"
  actionTable[92][63][1]="52"
  
  #-----------State 93-----------------
  actionTable[93][67][0]="R"
  actionTable[93][67][1]="53"

  actionTable[93][3][0]="R"
  actionTable[93][3][1]="53"

  actionTable[93][1][0]="R"
  actionTable[93][1][1]="53"

  actionTable[93][39][0]="R"
  actionTable[93][39][1]="53"

  actionTable[93][61][0]="R"
  actionTable[93][61][1]="53"

  actionTable[93][5][0]="R"
  actionTable[93][5][1]="53"

  actionTable[93][65][0]="R"
  actionTable[93][65][1]="53"

  actionTable[93][64][0]="R"
  actionTable[93][64][1]="53"

  actionTable[93][66][0]="R"
  actionTable[93][66][1]="53"

  actionTable[93][63][0]="R"
  actionTable[93][63][1]="53"
  
  #-----------State 94-----------------
  actionTable[94][67][0]="D"
  actionTable[94][67][1]="70"

  actionTable[94][3][0]="D"
  actionTable[94][3][1]="74"

  actionTable[94][1][0]="D"
  actionTable[94][1][1]="67"

  actionTable[94][39][0]="D"
  actionTable[94][39][1]="68"

  actionTable[94][61][0]="D"
  actionTable[94][61][1]="69"

  actionTable[94][5][0]="D"
  actionTable[94][5][1]="75"

  actionTable[94][65][0]="D"
  actionTable[94][65][1]="76"

  actionTable[94][64][0]="D"
  actionTable[94][64][1]="77"

  actionTable[94][66][0]="D"
  actionTable[94][66][1]="78"

  actionTable[94][63][0]="D"
  actionTable[94][63][1]="79"

  #-----------State 95-----------------
  actionTable[95][67][0]="R"
  actionTable[95][67][1]="56"

  actionTable[95][3][0]="R"
  actionTable[95][3][1]="56"

  actionTable[95][1][0]="R"
  actionTable[95][1][1]="56"

  actionTable[95][39][0]="R"
  actionTable[95][39][1]="56"

  actionTable[95][61][0]="R"
  actionTable[95][61][1]="56"

  actionTable[95][5][0]="R"
  actionTable[95][5][1]="56"

  actionTable[95][65][0]="R"
  actionTable[95][65][1]="56"

  actionTable[95][64][0]="R"
  actionTable[95][64][1]="56"

  actionTable[95][66][0]="R"
  actionTable[95][66][1]="56"

  actionTable[95][63][0]="R"
  actionTable[95][63][1]="56"
  #-----------State 96-----------------
  actionTable[96][67][0]="R"
  actionTable[96][67][1]="57"

  actionTable[96][3][0]="R"
  actionTable[96][3][1]="57"

  actionTable[96][1][0]="R"
  actionTable[96][1][1]="57"

  actionTable[96][39][0]="R"
  actionTable[96][39][1]="57"

  actionTable[96][61][0]="R"
  actionTable[96][61][1]="57"

  actionTable[96][5][0]="R"
  actionTable[96][5][1]="57"

  actionTable[96][65][0]="R"
  actionTable[96][65][1]="57"

  actionTable[96][64][0]="R"
  actionTable[96][64][1]="57"

  actionTable[96][66][0]="R"
  actionTable[96][66][1]="57"

  actionTable[96][63][0]="R"
  actionTable[96][63][1]="57"
  
  #-----------State 97-----------------
  actionTable[97][67][0]="R"
  actionTable[97][67][1]="57"

  actionTable[97][3][0]="R"
  actionTable[97][3][1]="57"

  actionTable[97][1][0]="R"
  actionTable[97][1][1]="57"

  actionTable[97][39][0]="R"
  actionTable[97][39][1]="57"

  actionTable[97][61][0]="R"
  actionTable[97][61][1]="57"

  actionTable[97][5][0]="R"
  actionTable[97][5][1]="57"

  actionTable[97][65][0]="R"
  actionTable[97][65][1]="57"

  actionTable[97][64][0]="R"
  actionTable[97][64][1]="57"

  actionTable[97][66][0]="R"
  actionTable[97][66][1]="57"

  actionTable[97][63][0]="R"
  actionTable[97][63][1]="57"
  
  #-----------State 98-----------------
  actionTable[98][67][0]="R"
  actionTable[98][67][1]="59"

  actionTable[98][3][0]="R"
  actionTable[98][3][1]="59"

  actionTable[98][1][0]="R"
  actionTable[98][1][1]="59"

  actionTable[98][39][0]="R"
  actionTable[98][39][1]="59"

  actionTable[98][61][0]="R"
  actionTable[98][61][1]="59"

  actionTable[98][5][0]="R"
  actionTable[98][5][1]="59"

  actionTable[98][65][0]="R"
  actionTable[98][65][1]="59"

  actionTable[98][64][0]="R"
  actionTable[98][64][1]="59"

  actionTable[98][66][0]="R"
  actionTable[98][66][1]="59"

  actionTable[98][63][0]="R"
  actionTable[98][63][1]="59"

  #---------------------Giuseppe------------------------------
  actionTable[99][67][0] = "D"
  actionTable[99][67][1] = "70"

  actionTable[99][3][0] = "D"
  actionTable[99][3][1] = "74"

  actionTable[99][1][0] = "D"
  actionTable[99][1][1] = "67"

  actionTable[99][39][0] = "D"
  actionTable[99][39][1] = "68"

  actionTable[99][61][0] = "D"
  actionTable[99][61][1] = "69"
  
  actionTable[99][5][0] = "D"
  actionTable[99][5][1] = "75"

  actionTable[99][65][0] = "D"
  actionTable[99][65][1] = "76"

  actionTable[99][64][0] = "D"
  actionTable[99][64][1] = "77"

  actionTable[99][66][0] = "D"
  actionTable[99][66][1] = "78"

  actionTable[99][63][0] = "D"
  actionTable[99][63][1] = "79"

  actionTable[100][67][0] = "R"
  actionTable[100][67][1] = "62"

  actionTable[100][3][0] = "R"
  actionTable[100][3][1] = "62"

  actionTable[100][1][0] = "R"
  actionTable[100][1][1] = "62"

  actionTable[100][39][0] = "R"
  actionTable[100][39][1] = "62"

  actionTable[100][61][0] = "R"
  actionTable[100][61][1] = "62"

  actionTable[100][5][0] = "R"
  actionTable[100][5][1] = "62"

  actionTable[100][65][0] = "R"
  actionTable[100][65][1] = "62"

  actionTable[100][64][0] = "R"
  actionTable[100][64][1] = "62"

  actionTable[100][66][0] = "R"
  actionTable[100][66][1] = "62"

  actionTable[100][63][0] = "R"
  actionTable[100][63][1] = "62"

  actionTable[101][67][0] = "R"
  actionTable[101][67][1] = "63"

  actionTable[101][67][0] = "R"
  actionTable[101][67][1] = "63"

  actionTable[101][3][0] = "R"
  actionTable[101][3][1] = "63"

  actionTable[101][1][0] = "R"
  actionTable[101][1][1] = "63"

  actionTable[101][39][0] = "R"
  actionTable[101][39][1] = "63"

  actionTable[101][61][0] = "R"
  actionTable[101][61][1] = "63"

  actionTable[101][5][0] = "R"
  actionTable[101][5][1] = "63"

  actionTable[101][65][0] = "R"
  actionTable[101][65][1] = "63"

  actionTable[101][64][0] = "R"
  actionTable[101][64][1] = "63"

  actionTable[101][66][0] = "R"
  actionTable[101][66][1] = "63"

  actionTable[101][63][0] = "R"
  actionTable[101][63][1] = "63"

  actionTable[102][67][0] = "D"
  actionTable[102][67][1] = "70"

  actionTable[102][3][0] = "D"
  actionTable[102][3][1] = "74"

  actionTable[102][1][0] = "D"
  actionTable[102][1][1] = "67"

  actionTable[102][39][0] = "D"
  actionTable[102][39][1] = "68"
  
  actionTable[102][61][0] = "D"
  actionTable[102][61][1] = "69"

  actionTable[102][5][0] = "D"
  actionTable[102][5][1] = "75"

  actionTable[102][65][0] = "D"
  actionTable[102][65][1] = "76"

  actionTable[102][64][0] = "D"
  actionTable[102][64][1] = "77"

  actionTable[102][66][0] = "D"
  actionTable[102][66][1] = "78"

  actionTable[102][63][0] = "D"
  actionTable[102][63][1] = "79"

  actionTable[103][67][0] = "R"
  actionTable[103][67][1] = "66"

  actionTable[103][3][0] = "R"
  actionTable[103][3][1] = "66"

  actionTable[103][1][0] = "R"
  actionTable[103][1][1] = "66"

  actionTable[103][39][0] = "R"
  actionTable[103][39][1] = "66"

  actionTable[103][61][0] = "R"
  actionTable[103][61][1] = "66"

  actionTable[103][5][0] = "R"
  actionTable[103][5][1] = "66"

  actionTable[103][65][0] = "R"
  actionTable[103][65][1] = "66"

  actionTable[103][64][0] = "R"
  actionTable[103][64][1] = "66"

  actionTable[103][66][0] = "R"
  actionTable[103][66][1] = "66"

  actionTable[103][63][0] = "R"
  actionTable[103][63][1] = "66"

  actionTable[104][67][0] = "R"
  actionTable[104][67][1] = "67"

  actionTable[104][3][0] = "R"
  actionTable[104][3][1] = "67"

  actionTable[104][1][0] = "R"
  actionTable[104][1][1] = "67"

  actionTable[104][39][0] = "R"
  actionTable[104][39][1] = "67"

  actionTable[104][61][0] = "R"
  actionTable[104][61][1] = "67"

  actionTable[104][5][0] = "R"
  actionTable[104][5][1] = "67"

  actionTable[104][65][0] = "R"
  actionTable[104][65][1] = "67"

  actionTable[104][64][0] = "R"
  actionTable[104][64][1] = "67"

  actionTable[104][66][0] = "R"
  actionTable[104][66][1] = "67"

  actionTable[104][63][0] = "R"
  actionTable[104][63][1] = "67"

  actionTable[105][67][0] = "R"
  actionTable[105][67][1] = "68"

  actionTable[105][3][0] = "R"
  actionTable[105][3][1] = "68"

  actionTable[105][1][0] = "R"
  actionTable[105][1][1] = "68"

  actionTable[105][39][0] = "R"
  actionTable[105][39][1] = "68"

  actionTable[105][61][0] = "R"
  actionTable[105][61][1] = "68"

  actionTable[105][5][0] = "R"
  actionTable[105][5][1] = "68"

  actionTable[105][65][0] = "R"
  actionTable[105][65][1] = "68"

  actionTable[105][64][0] = "R"
  actionTable[105][64][1] = "68"

  actionTable[105][66][0] = "R"
  actionTable[105][66][1] = "68"

  actionTable[105][63][0] = "R"
  actionTable[105][63][1] = "68"

  actionTable[106][69][0] = "R"
  actionTable[106][69][1] = "69"

  actionTable[106][13][0] = "R"
  actionTable[106][13][1] = "69"

  actionTable[106][2][0] = "R"
  actionTable[106][2][1] = "69"

  actionTable[106][4][0] = "R"
  actionTable[106][4][1] = "69"

  actionTable[106][41][0] = "R"
  actionTable[106][41][1] = "69"

  actionTable[106][40][0] = "R"
  actionTable[106][40][1] = "69"

  actionTable[106][25][0] = "R"
  actionTable[106][25][1] = "69"

  actionTable[106][24][0] = "R"
  actionTable[106][24][1] = "69"

  actionTable[106][20][0] = "R"
  actionTable[106][20][1] = "69"

  actionTable[106][22][0] = "R"
  actionTable[106][22][1] = "69"

  actionTable[106][21][0] = "R"
  actionTable[106][21][1] = "69"

  actionTable[106][23][0] = "R"
  actionTable[106][23][1] = "69"

  actionTable[106][1][0] = "R"
  actionTable[106][1][1] = "69"

  actionTable[106][39][0] = "R"
  actionTable[106][39][1] = "69"

  actionTable[106][9][0] = "R"
  actionTable[106][9][1] = "69"

  actionTable[106][11][0] = "R"
  actionTable[106][11][1] = "69"

  actionTable[106][10][0] = "R"
  actionTable[106][10][1] = "69"

  actionTable[107][4][0] = "D"
  actionTable[107][4][1] = "122"

  actionTable[108][6][0] = "D"
  actionTable[108][6][1] = "123"

  actionTable[109][13][0] = "R"
  actionTable[109][13][1] = "27"

  actionTable[109][67][0] = "R"
  actionTable[109][67][1] = "27"

  actionTable[109][8][0] = "R"
  actionTable[109][8][1] = "27"

  actionTable[109][49][0] = "R"
  actionTable[109][49][1] = "27"

  actionTable[109][50][0] = "R"
  actionTable[109][50][1] = "27"

  actionTable[109][51][0] = "R"
  actionTable[109][51][1] = "27"

  actionTable[109][54][0] = "R"
  actionTable[109][54][1] = "27"

  actionTable[109][38][0] = "R"
  actionTable[109][38][1] = "27"

  actionTable[109][57][0] = "R"
  actionTable[109][57][1] = "27"

  actionTable[110][69][0] = "R"
  actionTable[110][69][1] = "31"

  actionTable[110][13][0] = "R"
  actionTable[110][13][1] = "31"

  actionTable[110][2][0] = "R"
  actionTable[110][2][1] = "31"

  actionTable[110][4][0] = "R"
  actionTable[110][4][1] = "31"

  actionTable[110][41][0] = "R"
  actionTable[110][41][1] = "31"

  actionTable[110][40][0] = "R"
  actionTable[110][40][1] = "31"

  actionTable[110][25][0] = "R"
  actionTable[110][25][1] = "31"

  actionTable[110][24][0] = "R"
  actionTable[110][24][1] = "31"

  actionTable[110][20][0] = "R"
  actionTable[110][20][1] = "31"

  actionTable[110][22][0] = "R"
  actionTable[110][22][1] = "31"

  actionTable[110][21][0] = "R"
  actionTable[110][21][1] = "31"

  actionTable[110][23][0] = "R"
  actionTable[110][23][1] = "31"

  actionTable[110][1][0] = "R"
  actionTable[110][1][1] = "31"

  actionTable[110][39][0] = "R"
  actionTable[110][39][1] = "31"

  actionTable[110][9][0] = "R"
  actionTable[110][9][1] = "31"

  actionTable[110][11][0] = "R"
  actionTable[110][11][1] = "31"

  actionTable[110][10][0] = "R"
  actionTable[110][10][1] = "31"

  actionTable[111][4][0] = "R"
  actionTable[111][4][1] = "32"

  actionTable[111][6][0] = "R"
  actionTable[111][6][1] = "32"

  actionTable[112][67][0] = "D"
  actionTable[112][67][1] = "70"

  actionTable[112][3][0] = "D"
  actionTable[112][3][1] = "74"

  actionTable[112][1][0] = "D"
  actionTable[112][1][1] = "67"

  actionTable[112][39][0] = "D"
  actionTable[112][39][1] = "68"

  actionTable[112][61][0] = "D"
  actionTable[112][61][1] = "69"

  actionTable[112][5][0] = "D"
  actionTable[112][5][1] = "75"

  actionTable[112][65][0] = "D"
  actionTable[112][65][1] = "76"

  actionTable[112][64][0] = "D"
  actionTable[112][64][1] = "77"

  actionTable[112][66][0] = "D"
  actionTable[112][66][1] = "78"

  actionTable[112][63][0] = "D"
  actionTable[112][63][1] = "79"

  actionTable[113][4][0] = "R"
  actionTable[113][4][1] = "35"

  actionTable[113][6][0] = "R"
  actionTable[113][6][1] = "35"

  actionTable[114][7][0] = "D"
  actionTable[114][7][1] = "125"

  actionTable[115][13][0] = "R"
  actionTable[115][13][1] = "41"

  actionTable[115][67][0] = "R"
  actionTable[115][67][1] = "41"

  actionTable[115][8][0] = "R"
  actionTable[115][8][1] = "41"

  actionTable[115][49][0] = "R"
  actionTable[115][49][1] = "41"

  actionTable[115][50][0] = "R"
  actionTable[115][50][1] = "41"

  actionTable[115][51][0] = "R"
  actionTable[115][51][1] = "41"

  actionTable[115][54][0] = "R"
  actionTable[115][54][1] = "41"

  actionTable[115][38][0] = "R"
  actionTable[115][38][1] = "41"

  actionTable[115][57][0] = "R"
  actionTable[115][57][1] = "41"

  actionTable[116][69][0] = "R"
  actionTable[116][69][1] = "46"

  actionTable[116][13][0] = "R"
  actionTable[116][13][1] = "46"

  actionTable[116][2][0] = "R"
  actionTable[116][2][1] = "46"

  actionTable[116][4][0] = "R"
  actionTable[116][4][1] = "46"

  actionTable[116][41][0] = "R"
  actionTable[116][41][1] = "46"

  actionTable[116][40][0] = "D"
  actionTable[116][40][1] = "90"

  actionTable[117][69][0] = "R"
  actionTable[117][69][1] = "48"

  actionTable[117][13][0] = "R"
  actionTable[117][13][1] = "48"

  actionTable[117][2][0] = "R"
  actionTable[117][2][1] = "48"

  actionTable[117][4][0] = "R"
  actionTable[117][4][1] = "48"

  actionTable[117][41][0] = "R"
  actionTable[117][41][1] = "48"

  actionTable[117][40][0] = "R"
  actionTable[117][40][1] = "48"

  actionTable[117][25][0] = "D"
  actionTable[117][25][1] = "92"

  actionTable[117][24][0] = "D"
  actionTable[117][24][1] = "93"

  actionTable[118][69][0] = "R"
  actionTable[118][69][1] = "50"

  actionTable[118][13][0] = "R"
  actionTable[118][13][1] = "50"

  actionTable[118][2][0] = "R"
  actionTable[118][2][1] = "50"

  actionTable[118][4][0] = "R"
  actionTable[118][4][1] = "50"

  actionTable[118][41][0] = "R"
  actionTable[118][41][1] = "50"

  actionTable[118][40][0] = "R"
  actionTable[118][40][1] = "50"

  actionTable[118][25][0] = "R"
  actionTable[118][25][1] = "50"

  actionTable[118][24][0] = "R"
  actionTable[118][24][1] = "50"

  actionTable[118][20][0] = "D"
  actionTable[118][20][1] = "95"

  actionTable[118][22][0] = "D"
  actionTable[118][22][1] = "96"

  actionTable[118][21][0] = "D"
  actionTable[118][21][1] = "97"

  actionTable[118][23][0] = "D"
  actionTable[118][23][1] = "98"

  actionTable[119][69][0] = "R"
  actionTable[119][69][1] = "54"

  actionTable[119][13][0] = "R"
  actionTable[119][13][1] = "54"

  actionTable[119][2][0] = "R"
  actionTable[119][2][1] = "54"

  actionTable[119][4][0] = "R"
  actionTable[119][4][1] = "54"

  actionTable[119][41][0] = "R"
  actionTable[119][41][1] = "54"

  actionTable[119][40][0] = "R"
  actionTable[119][40][1] = "54"

  actionTable[119][25][0] = "R"
  actionTable[119][25][1] = "54"

  actionTable[119][24][0] = "R"
  actionTable[119][24][1] = "54"

  actionTable[119][20][0] = "R"
  actionTable[119][20][1] = "54"

  actionTable[119][22][0] = "R"
  actionTable[119][22][1] = "54"

  actionTable[119][21][0] = "R"
  actionTable[119][21][1] = "54"

  actionTable[119][23][0] = "R"
  actionTable[119][23][1] = "54"

  actionTable[119][1][0] = "D"
  actionTable[119][1][1] = "100"

  actionTable[119][39][0] = "D"
  actionTable[119][39][1] = "101"

  actionTable[120][69][0] = "R"
  actionTable[120][69][1] = "60"

  actionTable[120][13][0] = "R"
  actionTable[120][13][1] = "60"

  actionTable[120][2][0] = "R"
  actionTable[120][2][1] = "60"

  actionTable[120][4][0] = "R"
  actionTable[120][4][1] = "60"

  actionTable[120][41][0] = "R"
  actionTable[120][41][1] = "60"

  actionTable[120][40][0] = "R"
  actionTable[120][40][1] = "60"

  actionTable[120][25][0] = "R"
  actionTable[120][25][1] = "60"

  actionTable[120][24][0] = "R"
  actionTable[120][24][1] = "60"

  actionTable[120][20][0] = "R"
  actionTable[120][20][1] = "60"

  actionTable[120][22][0] = "R"
  actionTable[120][22][1] = "60"

  actionTable[120][21][0] = "R"
  actionTable[120][21][1] = "60"

  actionTable[120][23][0] = "R"
  actionTable[120][23][1] = "60"

  actionTable[120][1][0] = "R"
  actionTable[120][1][1] = "60"

  actionTable[120][39][0] = "R"
  actionTable[120][39][1] = "60"

  actionTable[120][9][0] = "D"
  actionTable[120][9][1] = "103"

  actionTable[120][11][0] = "D"
  actionTable[120][11][1] = "104"

  actionTable[120][10][0] = "D"
  actionTable[120][10][1] = "105"

  actionTable[121][69][0] = "R"
  actionTable[121][69][1] = "64"

  actionTable[121][13][0] = "R"
  actionTable[121][13][1] = "64"
  
  actionTable[121][2][0] = "R"
  actionTable[121][2][1] = "64"

  actionTable[121][4][0] = "R"
  actionTable[121][4][1] = "64"

  actionTable[121][41][0] = "R"
  actionTable[121][41][1] = "64"

  actionTable[121][40][0] = "R"
  actionTable[121][40][1] = "64"

  actionTable[121][25][0] = "R"
  actionTable[121][25][1] = "64"

  actionTable[121][24][0] = "R"
  actionTable[121][24][1] = "64"

  actionTable[121][20][0] = "R"
  actionTable[121][20][1] = "64"

  actionTable[121][22][0] = "R"
  actionTable[121][22][1] = "64"

  actionTable[121][21][0] = "R"
  actionTable[121][21][1] = "64"

  actionTable[121][23][0] = "R"
  actionTable[121][23][1] = "64"

  actionTable[121][1][0] = "R"
  actionTable[121][1][1] = "64"

  actionTable[121][39][0] = "R"
  actionTable[121][39][1] = "64"

  actionTable[121][9][0] = "R"
  actionTable[121][9][1] = "64"

  actionTable[121][11][0] = "R"
  actionTable[121][11][1] = "64"

  actionTable[121][10][0] = "R"
  actionTable[121][10][1] = "64"

  actionTable[122][69][0] = "R"
  actionTable[122][69][1] = "78"

  actionTable[122][13][0] = "R"
  actionTable[122][13][1] = "78"

  actionTable[122][2][0] = "R"
  actionTable[122][2][1] = "78"

  actionTable[122][4][0] = "R"
  actionTable[122][4][1] = "78"

  actionTable[122][41][0] = "R"
  actionTable[122][41][1] = "78"

  actionTable[122][40][0] = "R"
  actionTable[122][40][1] = "78"

  actionTable[122][25][0] = "R"
  actionTable[122][25][1] = "78"

  actionTable[122][24][0] = "R"
  actionTable[122][24][1] = "78"

  actionTable[122][20][0] = "R"
  actionTable[122][20][1] = "78"

  actionTable[122][22][0] = "R"
  actionTable[122][22][1] = "78"

  actionTable[122][21][0] = "R"
  actionTable[122][21][1] = "78"

  actionTable[122][23][0] = "R"
  actionTable[122][23][1] = "78"

  actionTable[122][1][0] = "R"
  actionTable[122][1][1] = "78"

  actionTable[122][39][0] = "R"
  actionTable[122][39][1] = "78"

  actionTable[122][9][0] = "R"
  actionTable[122][9][1] = "78"

  actionTable[122][11][0] = "R"
  actionTable[122][11][1] = "78"

  actionTable[122][10][0] = "R"
  actionTable[122][10][1] = "78"

  actionTable[123][69][0] = "R"
  actionTable[123][69][1] = "79"

  actionTable[123][13][0] = "R"
  actionTable[123][13][1] = "79"

  actionTable[123][2][0] = "R"
  actionTable[123][2][1] = "79"

  actionTable[123][4][0] = "R"
  actionTable[123][4][1] = "79"

  actionTable[123][41][0] = "R"
  actionTable[123][41][1] = "79"

  actionTable[123][40][0] = "R"
  actionTable[123][40][1] = "79"

  actionTable[123][25][0] = "R"
  actionTable[123][25][1] = "79"

  actionTable[123][24][0] = "R"
  actionTable[123][24][1] = "79"

  actionTable[123][20][0] = "R"
  actionTable[123][20][1] = "79"

  actionTable[123][22][0] = "R"
  actionTable[123][22][1] = "79"

  actionTable[123][21][0] = "R"
  actionTable[123][21][1] = "79"

  actionTable[123][23][0] = "R"
  actionTable[123][23][1] = "79"

  actionTable[123][1][0] = "R"
  actionTable[123][1][1] = "79"

  actionTable[123][39][0] = "R"
  actionTable[123][39][1] = "79"

  actionTable[123][9][0] = "R"
  actionTable[123][9][1] = "79"

  actionTable[123][11][0] = "R"
  actionTable[123][11][1] = "79"

  actionTable[123][10][0] = "R"
  actionTable[123][10][1] = "79"

  actionTable[124][69][0] = "D"
  actionTable[124][69][1] = "113"

  actionTable[124][69][0] = "D"
  actionTable[124][69][1] = "113"

  actionTable[124][2][0] = "D"
  actionTable[124][2][1] = "112"

  actionTable[125][69][0] = "D"
  actionTable[125][69][1] = "28"

  actionTable[126][4][0] = "R"
  actionTable[126][4][1] = "34"

  actionTable[126][6][0] = "R"
  actionTable[126][6][1] = "34"

  actionTable[127][13][0] = "D"
  actionTable[127][13][1] = "48"

  actionTable[127][67][0] = "D"
  actionTable[127][67][1] = "40"

  actionTable[127][8][0] = "D"
  actionTable[127][8][1] = "128"

  actionTable[127][49][0] = "D"
  actionTable[127][49][1] = "41"

  actionTable[127][50][0] = "D"
  actionTable[127][50][1] = "42"

  actionTable[127][51][0] = "D"
  actionTable[127][51][0] = "44"

  actionTable[127][54][0] = "D"
  actionTable[127][54][1] = "45"

  actionTable[127][38][0] = "D"
  actionTable[127][38][1] = "46"

  actionTable[127][57][0] = "D"
  actionTable[127][57][1] = "47"

  actionTable[128][69][0] = "D"
  actionTable[128][69][1] = "130"

  actionTable[129][69][0] = "D"
  actionTable[129][69][1] = "134"

  actionTable[129][53][0] = "D"
  actionTable[129][53][1] = "132"

  actionTable[129][52][0] = "D"
  actionTable[129][52][1] = "133"

  actionTable[130][69][0] = "R"
  actionTable[130][69][1] = "38"

  actionTable[130][53][0] = "R"
  actionTable[130][53][1] = "38"

  actionTable[130][52][0] = "R"
  actionTable[130][52][1] = "38"

  actionTable[131][13][0] = "R"
  actionTable[131][13][1] = "36"

  actionTable[131][67][0] = "R"
  actionTable[131][67][1] = "36"

  actionTable[131][8][0] = "R"
  actionTable[131][8][1] = "36"

  actionTable[131][49][0] = "R"
  actionTable[131][49][1] = "36"

  actionTable[131][50][0] = "R"
  actionTable[131][50][1] = "36"

  actionTable[131][51][0] = "R"
  actionTable[131][51][1] = "36"

  actionTable[131][54][0] = "R"
  actionTable[131][54][1] = "36"

  actionTable[131][38][0] = "R"
  actionTable[131][38][1] = "36"

  actionTable[131][57][0] = "R"
  actionTable[131][57][1] = "36"

  actionTable[132][3][0] = "D"
  actionTable[132][3][1] = "135"

  actionTable[133][7][0] = "D"
  actionTable[133][7][1] = "136"

  actionTable[134][13][0] = "R"
  actionTable[134][13][1] = "40"

  actionTable[134][67][0] = "R"
  actionTable[134][67][1] = "40"

  actionTable[134][67][0] = "R"
  actionTable[134][67][1] = "40"

  actionTable[134][8][0] = "R"
  actionTable[134][8][1] = "40"

  actionTable[134][49][0] = "R"
  actionTable[134][49][1] = "40"

  actionTable[134][50][0] = "R"
  actionTable[134][50][1] = "40"

  actionTable[134][51][0] = "R"
  actionTable[134][51][1] = "40"

  actionTable[134][54][0] = "R"
  actionTable[134][54][1] = "40"

  actionTable[134][38][0] = "R"
  actionTable[134][38][1] = "40"
  
  actionTable[134][57][0] = "R"
  actionTable[134][57][1] = "40"

  actionTable[135][67][0] = "D"
  actionTable[135][67][1] = "70"

  actionTable[135][3][0] = "D"
  actionTable[135][3][1] = "74"

  actionTable[135][1][0] = "D"
  actionTable[135][1][1] = "67"

  actionTable[135][39][0] = "D"
  actionTable[135][39][1] = "68"

  actionTable[135][61][0] = "D"
  actionTable[135][61][1] = "69"

  actionTable[135][5][0] = "D"
  actionTable[135][5][1] = "75"

  actionTable[135][65][0] = "D"
  actionTable[135][65][1] = "76"

  actionTable[135][64][0] = "D"
  actionTable[135][64][1] = "77"

  actionTable[135][66][0] = "D"
  actionTable[135][66][1] = "78"

  actionTable[135][63][0] = "D"
  actionTable[135][63][1] = "79"

  actionTable[136][69][0] = "D"
  actionTable[136][69][1] = "28"

  actionTable[137][4][0] = "D"
  actionTable[137][4][1] = "139"

  actionTable[138][13][0] = "D"
  actionTable[138][13][1] = "48"

  actionTable[138][67][0] = "D"
  actionTable[138][67][1] = "40"

  actionTable[138][8][0] = "D"
  actionTable[138][8][1] = "140"

  actionTable[138][49][0] = "D"
  actionTable[138][49][1] = "41"

  actionTable[138][50][0] = "D"
  actionTable[138][50][1] = "42"

  actionTable[138][51][0] = "D"
  actionTable[138][51][1] = "44"

  actionTable[138][54][0] = "D"
  actionTable[138][54][1] = "45"

  actionTable[138][38][0] = "D"
  actionTable[138][38][1] = "46"

  actionTable[138][57][0] = "D"
  actionTable[138][57][1] = "47"

  actionTable[139][7][0] = "D"
  actionTable[139][7][1] = "141"

  actionTable[140][13][0] = "R"
  actionTable[140][13][1] = "39"

  actionTable[140][67][0] = "R"
  actionTable[140][67][1] = "39"

  actionTable[140][8][0] = "R"
  actionTable[140][8][1] = "39"

  actionTable[140][49][0] = "R"
  actionTable[140][49][1] = "39"

  actionTable[140][50][0] = "R"
  actionTable[140][50][1] = "39"

  actionTable[140][51][0] = "R"
  actionTable[140][51][1] = "39"

  actionTable[140][54][0] = "R"
  actionTable[140][54][1] = "39"

  actionTable[140][38][0] = "R"
  actionTable[140][38][1] = "39"

  actionTable[140][57][0] = "R"
  actionTable[140][57][1] = "39"

  actionTable[141][69][0] = "D"
  actionTable[141][69][1] = "28"

  actionTable[142][13][0] = "D"
  actionTable[142][13][1] = "48"

  actionTable[142][67][0] = "D"
  actionTable[142][67][1] = "40"

  actionTable[142][8][0] = "D"
  actionTable[142][8][1] = "143"

  actionTable[142][49][0] = "D"
  actionTable[142][49][1] = "41"

  actionTable[142][50][0] = "D"
  actionTable[142][50][1] = "42"

  actionTable[142][51][0] = "D"
  actionTable[142][51][1] = "44"

  actionTable[142][54][0] = "D"
  actionTable[142][54][1] = "45"

  actionTable[142][38][0] = "D"
  actionTable[142][38][1] = "46"

  actionTable[142][57][0] = "D"
  actionTable[142][57][1] = "47"

  actionTable[143][69][0] = "R"
  actionTable[143][69][1] = "37"

  actionTable[143][53][0] = "R"
  actionTable[143][53][1] = "37"

  actionTable[142][52][0] = "R"
  actionTable[143][52][1] = "37"

# Driver code
readFile()
lexicalAnalize()
print("Token list: ", tokenList)
syntacticalAnalize()
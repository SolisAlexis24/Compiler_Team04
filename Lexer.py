import sys
from prettytable import PrettyTable
global code
code = ""
Token = {"keyword":[], "identifier":[],  "operator":[], "constant":[], "puctuation":[]} #It will have the form {type:[value1, value2, ..., valueN]}
global symbolTable
symbolTable = {"if": None, "else":None}
T_kw = ["int", "bool", "if", "else", "return", "true", "false"] #Token type keyword (RESERVED WORDS)
T_op = ["+", "-", "/", "**", "*", "^" , "|" , "~","<", ">", "<=", ">=", "==", "!=", "="] #Token type operator
T_punct = [";", "(", ")", "{", "}"] #Token type punctuation
Comment = "@" #Comment
numbers = "0123456789"
letters = "abcdefghijklmnopqrstuvwxyz"


def codeGetter():
    """This function read the content of a file and store the content onto the "code" variable"""
    global code
    if(len(sys.argv)!= 2): #This line tests if the number of elements in the list of arguments from the command line is equal to two, this is because the first argument is the Python file name, and the second must be our file name
        sys.exit()
    else:
        file_name = sys.argv[1]
        with open(file_name) as file:
            for line in file.readlines():
                
                code = code + line #Open the file and line by line, it reads the content and concatenate each line onto the string "code"

class Lexer:
    def __init__(self, codeIn):
        self.codeString = codeIn #Set the string to analize as the code that the function "codeGetter" gets
        self.currentPos = -1 #The initial position for the lexer is -1 (The method advance will update this inmediatly)
        self.peekPos = -1
        self.currentChar = None #The initial char of the lexer is None (The method advance will update this inmediatly)
        self.peekChar = None 
        self.line = 1
        self.buffer = ""
        self.flag = 0 #flag that indicates the incoming operation: 0=nothing, 1=Declaration
        self.pile = []
        self.counter = 0

    def advanceCurrent(self):
        """this method made the current char advance a space"""
        self.currentPos += 1 
        if (self.currentPos < len(self.codeString)):
            self.currentChar = self.codeString[self.currentPos]
        else:
            self.currentChar = None

    def Peek(self):
        """this method made the peek char advance a space"""
        self.peekPos += 1 
        if (self.peekPos < len(self.codeString)):
            self.peekChar = self.codeString[self.peekPos]
        else:
            self.peekChar = None

    def equalize(self):
        """This method equalize both pointers position, the current char to the peek char"""
        self.currentPos = self.peekPos
        self.currentChar = self.peekChar

    def emptyBuffer(self):
        """This method empty the buffer"""
        self.buffer = ""

    def advance_eol(self):
        """This method advance untill it found the end of line"""
        while(self.peekChar != "\n"):
            self.Peek()
        self.Peek()

    def printTokens(self):
        """This method is for print the tokens found in th code as a pretty table"""
        table = PrettyTable() #create table
        keyMax = 0  #max num of element
        for key in Token.keys(): #block that calculates the max num of elements
            if (len(Token[key]) > keyMax):
                keyMax = len(Token[key]) 
        
        for key, value in Token.items(): #store elements in column
            while(len(value) < keyMax):
                value.append(" ") #If the elements are not equal to the maximum, add spaces
            table.add_column(key, value) #add elements in column
        print(table) #print table with elements
        table = PrettyTable()
        table.add_column("Total de tokens", [self.counter])
        print(table)


    def scan(self):
        if (self.peekChar != None): #Executes until reach the eof
            if (self.peekChar == " " or self.peekChar =="\t"): #The peek char looks forward if the char is a non-imprimible char.
                self.Peek() #Moves forward the peekchar
                self.equalize() #Equalize the both pointers
                self.scan() #Recursion

            elif (self.peekChar == Comment): #If detects the beginning of a coment 
                self.advance_eol() #Advance until the end of the line
                self.line += 1
                self.equalize() #Equalize the both pointers
                self.scan() #Recursion

            elif(self.peekChar == "\n"):
                self.line += 1
                self.Peek() #Moves forward the peekchar
                self.equalize() #Equalize the both pointers
                self.scan() #Recursion

    def scan(self):
        if (self.peekChar != None): #Executes until reach the eof
            if (self.peekChar == " " or self.peekChar =="\t"): #The peek char looks forward if the char is a non-imprimible char.
                self.Peek() #If it's, it moves forward
                self.equalize() #Equalize the both pointers
                self.scan() #Recursion

            elif (self.peekChar == Comment): #If detects the beginning of a coment 
                self.advance_eol() #Advance until the end of the line
                self.Peek() #Advance again to be in the next line
                self.line += 1 #Increment the atribute line
                self.equalize() #Equalize pointers
                self.scan() #Recursion

            elif(self.peekChar == "\n"):
                self.Peek() #Advance again to be in the next line
                self.line += 1 #Increment the atribute line
                self.equalize() #Equalize pointers
                self.scan() #Recursion

            elif(self.currentChar in letters): #If the lexeme begin with a letter         
                while((self.peekChar in letters) or (self.peekChar in numbers) or self.peekChar == '_'): #moves the peekChar until it found a whitespace. Look for the example 1 in the README file
                    self.buffer += self.peekChar #Store the chain onto a buffer
                    self.Peek() #Advance
                if (self.buffer in T_op): #If the buffer string is a operator (and, or, not)
                    if(not(self.buffer in Token["operator"])): #if is not still stored
                        Token["operator"].append(self.buffer) #Store it
                    self.counter += 1
                    self.emptyBuffer() #empty the buffer
                    self.equalize() #Equalize pointers
                    self.scan()
                elif (self.buffer in T_kw): #If the buffer string is a reserved word
                    if((self.buffer == "int" or self.buffer == "bool") and self.flag == 0):
                        self.flag = 1
                    elif((self.buffer == "int" or self.buffer == "bool") and self.flag == 1):
                        self.throwError(" ,after a type it must be an identifier")
                    if(not(self.buffer in Token["keyword"])): #if is not still stored
                        Token["keyword"].append(self.buffer) #Store it
                    self.counter += 1
                    self.emptyBuffer() #empty the buffer
                    self.equalize() #Equalize pointers
                    self.scan()
                else: #if the char is a letter and it is not a keyword, it is an identifier
                    if(not(self.buffer in symbolTable) and self.flag == 1):
                        if(not(self.buffer in Token["identifier"])): #if it is not stored already
                            Token["identifier"].append(self.buffer) #Store it
                            symbolTable[self.buffer]=self.line
                        self.counter += 1
                        self.flag = 0
                        self.emptyBuffer() #empty the buffer
                        self.equalize() #Equalize pointers
                        self.scan() #Recursion
                    elif(not(self.buffer in symbolTable) and self.flag == 0):
                        self.throwError(", identifier used before assignment")
                    else:
                        self.counter += 1
                        self.flag = 0
                        self.emptyBuffer() #empty the buffer
                        self.equalize() #Equalize pointers
                        self.scan() #Recursion
            elif (self.currentChar in T_punct):
                if (not(self.currentChar in Token["puctuation"])): #if it is not stored already
                    Token["puctuation"].append(self.currentChar) #Store it
                self.counter += 1
                self.emptyBuffer() #empty the buffer
                self.Peek() #Advance the peekchar
                self.equalize() #Equalize pointers
                self.scan() #Recursion 

            elif(self.currentChar in T_op): #if the current chat is in ["+", "-", "/", "", "*", "^" , "|" , "~","<", ">", "<=", ">=", "==", "!=", "="] 
                self.counter += 1 #Found a token
                self.Peek() #Peek to see if it is a two length token
                if(self.peekChar in T_op): #if it is
                    if(self.peekChar == "+" or self.peekChar == "-"): #if the following is a sign it could be a number
                        if(not(self.currentChar in Token["operator"])):
                            Token["operator"].append(self.currentChar)
                        self.Peek()
                    else:
                        self.buffer = self.currentChar + self.peekChar
                        if(not(self.buffer in Token["operator"])):
                            Token["operator"].append(self.buffer)
                        self.Peek()
                else:
                    if(not(self.currentChar in Token["operator"])): #if it isnt a two lenght operator
                        Token["operator"].append(self.currentChar)
                self.emptyBuffer() #empty the buffer
                self.equalize() #Equalize pointers
                self.scan() #Recursion

            elif (self.currentChar in numbers): #If the lexeme begin a digit
                while(self.peekChar in numbers): #moves the peekChar until it found a whitespace
                    self.buffer += self.peekChar #Store the chain onto a buffer
                    self.Peek() #Advance
                if (not(self.buffer in Token["constant"])): #if it is not stored already
                    Token["constant"].append(self.buffer) #Store it
                self.counter += 1
                self.emptyBuffer() #empty the buffer
                self.equalize() #Equalize pointers
                self.scan() #Recursion  

        else:
            return


    def throwError(self, errorMesage):
        print("Error in line " + str(self.line) + errorMesage)
        exit()



codeGetter()
Lexer1 = Lexer(code)
Lexer1.advanceCurrent()
Lexer1.Peek()
Lexer1.scan()
Lexer1.printTokens()

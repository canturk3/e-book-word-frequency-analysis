import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

#Function for finding the book and downloading the book's contents.
def GetBook(bookNum):
    #Loops until a valid book that has print version entered 
    while(True):
        bookName = input("Please enter the name of the {} book:".format(bookNum))
        bookName = bookName.strip()
        #Replaces spaces and apostrophes with the characters used in wikibooks urls    
        urlBook = bookName.replace("'","%27")
        urlBook = bookName.replace(" ","_")
        
        #requests.get retrieves and stores the data of the page, one of which is status_code
        #which informs if the request was successful or not
        page = requests.get("https://en.wikibooks.org/wiki/{}/Print_version".format(urlBook)) 
        if page.status_code != 404:
            break
        page = requests.get("https://en.wikibooks.org/wiki/{}/Print_Version".format(urlBook)) 
        if page.status_code != 404:
            break
        page = requests.get("https://en.wikibooks.org/wiki/{}/print_version".format(urlBook))
        if page.status_code != 404:
            break
        page = requests.get("https://en.wikibooks.org/wiki/{}/Printable_version".format(urlBook))
        if page.status_code != 404:
            break
        else:
            print('Please enter both a valid and a printable book on WikiBooks.')
            
    #Gets all of the html content of the page
    pageContent = BeautifulSoup(page.content,"html.parser")
    
    #This returns a string containing all of the text the book contains, and lowers the letters
    #(All of the text that are written inside p,h, pre, li ,th, td.. as such headers in html)
    book = pageContent.get_text().lower()
    return book, bookName

#Function for saving the book contents into a text file where the source code is.
def SaveBook(book,txtName):
    #soup.get_text() returns an 8-bit Unicode string. To be compatible, text must be opened with UTF-8 encoding.
    bookTxt = open("{}.txt".format(txtName),"w",encoding="utf-8")
    #Since get_text() returns a single string it can be directly written
    bookTxt.write(book)
    bookTxt.close()
    
#Function for getting and clearing all of the words for comparisons also removes stop words.
def GetWords(book):
    #Divides the book into words
    bookWords = book.split()
    #Clears all of the punctuations and numbers in the word list
    removeList = ["'","’",'"','!','^','+','%','&','/','(',')','=','?','*','_','-','<','>','£','#','$','½','{',
                  '[',']','}','\\','|','~','@',';',',','.',':','*','0','1','2','3','4','5','6','7','8','9']    
    bookWords_Clean = []
    for word in bookWords:
        replaceWord = ""
        #If a character in a word is found in removeList; replaces it with empty space
        for char in word:
            remove = False
            for symbol in removeList:
                #Stops searching after the character is found
                if(char == symbol):
                    remove = True
                    break
            if(remove == False):
                replaceWord += char
            #If remove is true replace with empty string
            else:
                replaceWord += " "
                
        if(replaceWord != ""):
            #Replacing with empty space then splitting from there is to avoid merging words
            subWords = replaceWord.split()
            for subword in subWords:
                #Discards one letter words
                if(len(subword) != 1):
                    bookWords_Clean.append(subword)
        
    #Gets English stopwords from nltk library
    stopWords = stopwords.words('english')
    
    #Removes stop words from the words list
    bookWords_Cleaner = [] 
    for word in bookWords_Clean:
        isStop = False
        #If word is found in stopWords list it is not appended to the new list
        for stop in stopWords:
            if(word == stop):
                isStop = True
                break
        if(isStop == False):
            bookWords_Cleaner.append(word)
    return bookWords_Cleaner

#Function that creates a dictionary that holds words as keys and frequencies as their values
def CreateDictionary(bookWords):
    freq_dict = {}
    for index in range(len(bookWords)):
        #This control is to prevent counting the same occurences of a word that was counted before
        if(bookWords[index] not in freq_dict.keys()):
            count = 0
            #Counts by starting from the taken word's index to the end of the word list
            restIndex = index
            for restIndices in range(restIndex,len(bookWords)):
                if(bookWords[index] == bookWords[restIndices]):
                    count += 1
                    
            freq_dict[bookWords[index]] = count
    return(freq_dict)

#Sorts the dictionary in a descending order by its values, using sorted method
def DescendingList(freq_dict):
    #.items() is referred key values; key is the function that will be called for comparisons,
    #uses nameless function (called lambda), x: x[1] which means chooses second index(the way of ordering)
    #Reverse arranges it to be in descending order
    frequency = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
    return frequency

#Function for finding distinct and common words between two word dictionaries
def CommonDistinctWords(dict1,dict2):
    common_dict = {}
    distinct_dict1 = {}
    distinct_dict2 = {}
    #If a word from first book is found in second book, adds it to the common words; if it is not found,
    #adds it to the distinct words of the first book
    for word1 in dict1:
        equals = False
        for word2 in dict2:
             if(word1 == word2):
                 common_dict[word1] = dict1[word1] + dict2[word2]
                 equals = True
                 break
        if(equals == False):
             distinct_dict1[word1] = dict1[word1]
             
    #If a word from the second book isn't found in the first book,
    #adds it to the distinct words of the second book
    for word2 in dict2:
        equals = False
        for word1 in dict1:
             if(word1 == word2):
                 equals = True
                 break
        if(equals == False):
             distinct_dict2[word2] = dict2[word2]
             
    return common_dict, distinct_dict1, distinct_dict2

#Function that asks user the amount of frequencies they would like to see
def AskAmount(maxWords):
    print("Please enter the amount of word frequencies you would like to see")
    #Loops until the number is an integer and smaller or equal to maximum word count
    while(True):
        try:
            amount = int(input("Amount:"))
            if(amount > maxWords):
                print("Please enter a number smaller than maximum word amount in the book")
            else:
                break
        except ValueError:
            print("Please enter an integer.")
            
    return amount

#Function used for printing one column descending lists
def OutputOneColumn(frequencies, amount):
    space = 1
    for number in range(amount):
        #Assigned words minimum 17 digits of space to print orderly
        if(len(frequencies[number][0]) < 17):
            space = 17 - len(frequencies[number][0])
            
        print("{: >3}".format(str(number + 1)) + " " + frequencies[number][0] + (" " * space) +
              str(frequencies[number][1]))
    
#The main function that will work if the user input is one
def OneBook():
    #Finds and downloads the book into a string and stores the book name written by the user
    book,bookName = GetBook("")
    #Saves the book in the path of the source code
    SaveBook(book,"book1")
    #Words with their number of occurences in a descending 2D list is created
    frequencies = DescendingList(CreateDictionary(GetWords(book)))
    
    #Gets amount of frequencies to be displayed
    amount = AskAmount(len(frequencies))
    print("\n BOOK 1:{}\n NO WORD\t     FREQ_1".format(bookName))
    #Function that prints the descending list
    OutputOneColumn(frequencies,amount)
    
#The main function that will work if the user input is two 
def TwoBooks():
    #Finds and downloads the books and stores their names, written by the user
    #Gets two different books from user
    while(True):
        book1,bookName1 = GetBook("first")
        book2,bookName2 = GetBook("second")
        if(book1 == book2):
            print("Please enter two different books")
        else:
             break
    #Saves the books in the path of the source code
    SaveBook(book1,"book1")
    SaveBook(book2,"book2")

    #Gets word frequencies of the books into dictionaries
    dict1 = CreateDictionary(GetWords(book1))
    dict2 = CreateDictionary(GetWords(book2))
    
    #Gets common and distinct words' dictionaries
    commonwords, distinct1, distinct2 = CommonDistinctWords(dict1,dict2)
    
    #Distinct and common dictionaries' descending lists
    commonFreq = DescendingList(commonwords)
    dist1Freq = DescendingList(distinct1)
    dist2Freq = DescendingList(distinct2)
    
    #Gets amount of frequencies to be displayed
    #To prevent index errors sets the maximum word number user can see to the smallest of the 3 outputs
    if(len(commonFreq) <= len(dist1Freq) and len(commonFreq) <= len(dist2Freq)):
        amount = AskAmount(len(commonwords.keys()))
           
    elif(len(dist1Freq) <= len(dist2Freq) and len(dist1Freq) <= len(commonFreq)):
        amount = AskAmount(len(dist1Freq))
        
    else:
        amount = AskAmount(len(dist2Freq))

    #COMMON WORDS OUTPUT
    print("\n BOOK 1:{}\n".format(bookName1) +
          " BOOK 2:{}\n".format(bookName2) +
          " COMMON WORDS\n NO WORD\t     FREQ_1  FREQ_2  FREQ_SUM")
    
    spaceWord = 1
    for number in range(amount):
        word = commonFreq[number][0]
        #Assigned spaces that words occupy minimum 17 digits, to print values orderly
        if(len(commonFreq[number][0]) < 17):
            spaceWord = 17 - len(word)
        #Assigned spaces that values occupy 8 digits, to print values orderly
        print("{: >3}".format(str(number + 1)) + " " + commonFreq[number][0] + (" " * spaceWord) +
            str(dict1[word]) + (" " * (8 - len(str(dict1[word]))) +
            str(dict2[word]) + (" " * (8 - len(str(dict2[word]))) + str(commonFreq[number][1]))))

    #FIRST BOOK DISTINCT WORDS
    print("\n BOOK 1:{}\n".format(bookName1) +
          " DISTINCT WORDS\n NO WORD\t     FREQ_1")
    #Function that prints the descending list
    OutputOneColumn(dist1Freq,amount)

    #SECOND BOOK DISTINCT WORDS
    print("\n BOOK 2:{}\n".format(bookName2) +
          " DISTINCT WORDS\n NO WORD\t     FREQ_2")
    #Function that prints the descending list
    OutputOneColumn(dist2Freq,amount)

def Main():
    #Decides how the program will work based on the user input
    print("To download and display word frequencies of a book:\n" +
          "Please write -> one.\n" +
          "To download and display common and distinct word frequencies of two books:\n" +
          "Please write -> two.")
    
    #Loops until a valid input is written, not case sensitive
    while(True):
        mode = input("Mode:").lower()
        if(mode == "one"):
            OneBook()
            break
        elif(mode == "two"):
            TwoBooks()
            break
        else:
            print("Please enter a valid input.")
Main() 

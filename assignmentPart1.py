from __future__ import division
__author__ = 'svijaykumar'
from random import shuffle

import nltk
import os
import re
import codecs
import itertools
import random
from datetime import datetime


genres = {} # it

children_unigram = {}
history_unigram = {}
crime_unigram = {}
children_probabilityVector = {}
history_probabilityVector = {}
crime_probabilityVector = {}

children_bigram = {}
history_bigram = {}
crime_bigram = {}

# ConstructUnigramForAllGenre() => it constructs unigram for all the genres using the helper function unigramConstruct
def ConstructUnigramForAllGenre():
    global children_unigram, history_unigram, crime_unigram, children_probabilityVector, history_probabilityVector, crime_probabilityVector
    for genre, tokenList in genres.items():
        parsedTokens = list(itertools.chain.from_iterable(tokenList))
        if(genre=='children'):
            children_unigram,children_probabilityVector = unigramsConstruct(parsedTokens)
        elif(genre=='history'):
            history_unigram , history_probabilityVector = unigramsConstruct(parsedTokens)
        elif(genre=='crime'):
            crime_unigram,crime_probabilityVector = unigramsConstruct(parsedTokens)
#unigramsConstruct(parsedTokens)=> helper function to compute unigram for each genre
#input => parsed tokens for a given genre
#output => word_count and probability of unigram created
def unigramsConstruct(parsedTokens):
    total_words = 0
    wordcount_unigram = {}
    unigram_word_probability = {}
    for word in parsedTokens:
        total_words += 1
        if word not in wordcount_unigram:
            wordcount_unigram[word] = 1
        else:
            wordcount_unigram[word] += 1
    items = wordcount_unigram.items()
    for word, count in items:
        unigram_word_probability[word] = count / total_words
    return wordcount_unigram,unigram_word_probability

#def nextWord_Unigram(genre) => Helper function used by generateSentence() to get the next expected word token in unigram sentence
#input=> genre for which next word need to be generated
#output=> next word in the corpus to create unigram sentence
def nextWord_Unigram(genre):
    cumulativeProb = 0.0
    global children_probabilityVector,history_probabilityVector,crime_probabilityVector
    if(genre=='children'):
        values = children_probabilityVector.values()
        items = children_probabilityVector.items()
    elif(genre=='history'):
        values = history_probabilityVector.values()
        items = history_probabilityVector.items()
    elif(genre=='crime'):
        values = crime_probabilityVector.values()
        items = crime_probabilityVector.items()
    rv = random.uniform(0, sum(values))
    for key, prob in items:
        cumulativeProb += prob
        if rv < cumulativeProb:
            return key
    return key

#def ConstructBigramForAllGenre(genre)=> it constructs bigram for all the genres using the helper function bigramConstruct
def ConstructBigramForAllGenre():
    global children_bigram, history_bigram, crime_bigram
    for genre,tokenList in genres.items():
        parsedTokens = list(itertools.chain.from_iterable(tokenList))
        if(genre=='children'):
            children_bigram= bigramConstruct(parsedTokens,genre)
        elif(genre=='history'):
            history_bigram = bigramConstruct(parsedTokens,genre)
        elif(genre=='crime'):
            crime_bigram = bigramConstruct(parsedTokens,genre)

#bigramsConstruct(parsedTokens)=> helper function to compute bigram for each genre
#input => parsed tokens for a given genre and the genre name
#output => bigram constructed for the given genre using the following:-
#(bigram[(nextWord|previousWord)] = count[(peviousWord nextWord)] / count[previousWord]

def bigramConstruct(parsedTokens,genre):
    total_word_pair=0
    wordcount_bigram={}
    temp_bigram = {}
    unigram_wordcount_vector = {}
    global children_unigram, history_unigram, crime_unigram
    for i, word in enumerate(parsedTokens[:-1]):
        total_word_pair+= 1
        word0 = parsedTokens[i]
        word1 = parsedTokens[i+1]
        pair = (word0,word1)
        if pair not in wordcount_bigram:
            wordcount_bigram[pair] = 1
        else:
            wordcount_bigram[pair] += 1

    items = wordcount_bigram.items()
    if(genre=='children'):
        unigram_wordcount_vector = children_unigram
    elif(genre=='crime'):
        unigram_wordcount_vector = crime_unigram
    elif(genre=='history'):
        unigram_wordcount_vector = history_unigram

    for wordpair, i in items:
        word0 = wordpair[0]
        word1 = wordpair[1]
        if word0 in unigram_wordcount_vector.keys():
            temp_bigram[(word0, word1)] = wordcount_bigram[(word0, word1)] / unigram_wordcount_vector[word0]
        else:
            temp_bigram[(word0, word1)] = wordcount_bigram[(word0, word1)]
    return temp_bigram

#def nextWord_Bigram(genre) => Helper function used by generateSentence() to get the next expected word token in a Bigram sentence
#input=> genre for which next word need to be generated and previous word for which we need to determine nextword from our bigram model
#output=> next word in the corpus to create bigram sentence
def nextWord_Bigram(previousWord, genre):
    global history_bigram, crime_bigram, children_bigram
    cumulativeProb = 0.0
    sum = 0.0
    i = 0.0
    templist = []
    bigram_model = {}
    key= ""
    if(genre=='history'):
        bigram_model = history_bigram
    elif(genre == 'children'):
        bigram_model = children_bigram
    elif(genre == 'crime'):
        bigram_model = crime_bigram
    items = bigram_model.items()
    for wordpair,i in items:
        if(wordpair[0]== previousWord):
            templist.append(wordpair[1])
            sum+=i;
    random.shuffle(templist);
    rv = random.uniform(0, sum)
    for followedWord in templist:
        cumulativeProb += bigram_model.get((previousWord,followedWord))
        if rv < cumulativeProb:
            return followedWord
	return followedWord

#def completeSentence(initialToken,genre)=> this function tries to complete a seed sentence in a given genre using bigram model constructed above
#input =>  seed sentence , genre
#output => complete sentence terminated with end token
def completeSentence(initialToken,genre):
    sentence = nltk.word_tokenize(initialToken.decode('utf-8'))
    previousWord = sentence[len(sentence) - 1]
    nextWord = nextWord_Bigram(previousWord, genre)
    while ((nextWord != '.') and (len(sentence)< 30)):
        sentence.append(nextWord)
        previousWord = nextWord
        nextWord = nextWord_Bigram(previousWord,genre)
    sentenceString = " ".join(sentence)
    print genre, " : ", sentenceString

#def generateSentence(n,genre): Utility function to generate unigram and bigram sentences for a given genre
#input=> ngram model(1=unigram, 2= bigram) and genre for sentence creation
#output=> generated unigram/bigram sentence terminated with end token
def generateSentence(n,genre):
    global children_probabilityVector,crime_probabilityVector,history_probabilityVector
    sentence = []
    unigram_model = {}
    if(genre=='children'):
        unigram_model = children_probabilityVector
    elif(genre=='history'):
        unigram_model = history_probabilityVector
    elif(genre=='crime'):
        unigram_model = crime_probabilityVector
    if n == 1:
        nextWord = nextWord_Unigram(genre)
        while ((nextWord != '.') and (len(sentence)< 30)):
            sentence.append(nextWord)
            nextWord = nextWord_Unigram(genre)
        sentenceString = " ".join(sentence)
        print genre, " : ", sentenceString, "."
    elif n == 2:
        previousWord = nextWord_Unigram(genre)
        sentence.append(previousWord)
        nextWord = nextWord_Bigram(previousWord,genre)
        while ((nextWord != '.') and (len(sentence)< 30)):
            sentence.append(nextWord)
            previousWord = nextWord
            nextWord = nextWord_Bigram(previousWord,genre)
        sentenceString = " ".join(sentence)
        print genre, " : ", sentenceString, "."
    else:
        print "Please enter n = 1 for unigram or 2 for bigram"



# Execution starts here
# fetch all the training set files for a particular genre and build corpus for that genre using NLTK tokenizer
src_folder = raw_input("Enter the absolute path of the corpus folder (i.e directory containing the different genre folders : ")
dirs = os.listdir(src_folder)
for subdir in dirs:
    sentences = []
    tokens = []
    files = os.listdir(os.path.join(src_folder, subdir))
    for file in files:
        current_file = os.path.join(src_folder,subdir,file)
        inputFile = codecs.open(current_file, 'r', 'utf-8-sig')
        for line in inputFile:
            line = line.strip()
            tokens.append(nltk.word_tokenize(line))
    genres[subdir] = tokens

print "Constructing unigram and bigram model for the corpus"
#Call utility function to construct unigram for the given genre
ConstructUnigramForAllGenre()
print "Done with unigram construction...!!!"
#Call utility function to construct bigram for the given genre
ConstructBigramForAllGenre()
print "Done with bigram construction...!!!"

#menu to input options from user
menu = {}
menu['1'] = "Generate random sentence using unigram model"
menu['2'] = "Generate random sentence using bigram model"
menu['3'] = "Generate sentence using bigram model with seed token/string"
menu['4'] = "Quit"
while True:
    options=menu.keys()
    options.sort()
    for entry in options:
        print entry, menu[entry]
    selection=raw_input("Please Select:")
    if selection =='1':
      unigram_genre = raw_input("Enter the genre: ")
      generateSentence(1,unigram_genre)
    elif selection == '2':
      bigram_genre = raw_input("Enter the genre: ")
      generateSentence(2,bigram_genre)
    elif selection == '3':
        bigram_genre = raw_input("Enter the genre to complete the bigram sentence prediction: ")
        initial_text = raw_input("Enter the seed string/token: ")
        completeSentence(initial_text,bigram_genre)
    elif selection == '4':
      break
    else:
      print "Unknown Option Selected!"

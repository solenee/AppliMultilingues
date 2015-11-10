#coding:utf-8

#-------------------------------
# Parse ts.xml file to save the
# test set into a CVS file
# separatation : " : "
#-------------------------------

# nomfichier \t hapax1 ; hapax2 ; hapax3 ... hapaxn (peut etre ;)

import re, sys, os
import xml.etree.ElementTree as ET
import codecs
from collections import defaultdict

d_hapax = {} # dict<en|fr|de, dict<filename, list of hapax> >
d_hapax["en"] = {}
d_hapax["fr"] = {}
d_hapax["de"] = {}

def loadIndex(lang) :
  index_file = "index."+lang
  with open(index_file, "r") as f :
    for line in f :
      loadIndexLine(d_hapax[lang], line)

def loadIndexLine(dico, index_line) :
  tmp = index_line.split["\t"]
  dico[tmp[0]] = tmp[1].split(";")

def index(file) :
  result = [file]
  dico = defaultdict(int)
  with open(file, "r") as f: #codecs.open(file, "r", "utf-8") as f:
    for line in f :
      #print line
      #print line.split("\n")
      dico[line.strip()] += 1
  #print dico
  hapax = [w for w in dico.keys() if dico[w] == 1]
  return ';'.join(hapax)

def forAllFiles(in_path, out_path) :
  with open(out_path, "w") as out_file:
    file_paths = os.listdir(in_path)
    for file_path in file_paths:
        out_file.write(file_path+"\t"+index(in_path + "/" + file_path)+'\n')

def parse(index_line) :
  tmp = index_line.split["\t"]
  src_name =tmp[0]
  h_src = tmp[1].split(";")
  lresult = [src_name, h_src]
  return lresult

def findCandidateScores(hapax_src, l_trgt_hapax, nb, similarityFunction) :
  """ nb : number of candidates scores to find """
  print "=====" #
  TOP = nb
  scores = [] #list<Double> ; invariant : len(scores) <= TOP
  candidates = {} #Map< Double, list<String> >
  result = [] #Concatenation of Strings from candidates, ordered by their rank; len(translations) <= TOP
  rank_results = [] #Concatenation of couple - rank
  current_min = 10000 #TODO initialize with max double
  for c in l_trgt_hapax :
    score_c = similarity(hapax_src, l_trgt_hapax[c], similarityFunction)
    if len(scores) < TOP :
      # add candidate
      #print "ADDING ("+c+", "+str(score_c)+")"
      if score_c not in candidates : 
        scores.append(score_c)
        candidates[score_c] = []
      # score_c is already in scores and in candidates' keyset
      candidates[score_c].append(c)
      # update current_min
      if current_min > score_c : current_min = score_c
    else :
      if score_c > current_min :
        # replace by the candidate c
        # pre : current_min is in candidates as key and in scores  
        scores.remove(current_min)
        del candidates[current_min]
        # add candidate
        #print "ADDING ("+c+", "+str(score_c)+")"
        if score_c not in candidates : 
          scores.append(score_c)
          candidates[score_c] = []
        #else score_c is already in scores and in candidates' keyset
        candidates[score_c].append(c)
        # update current_min
        current_min = min(scores)
  # rank the results
  print candidates #
  return candidates

def align(lsrc, ltrgt) :
  """ Write a result file """
  TOP = 5
  # create (filename, [hapaxes]) (separate function)
  load(lsrc)
  load(ltrgt)

  
  for file_src in d_hapax[lsrc].keys() :
    top5 = None #list of the 5 nearest files
    
    intersec = lambda x, y : len(set(x) & set(y))
    def normalizedIntersec(x, y) :
      s_x = set(x)
      s_y = set(y)
      return len(s_x & s_y)/len(s_x | s_y)

    # compute similarity between hapaxes lists (separate function)
    # memorize in dictionnary of lists the 5 best ones

    #1. baseline
    top5 = findCandidateScores(d_hapax[lsrc][file_src], d_hapax[ltrgt], TOP, intersec)
  
    print top5

def printResult(fil, top) :
  with open(fil, "r") as f:
    for i in range(top):
      print f.readline()      
  

if __name__ == "__main__":
  shouldIndex = False
  if shouldIndex :
    forAllFiles("Donnees/FR/fr", "Donnees/extracted/index.fr")
    forAllFiles("Donnees/EN/en", "Donnees/extracted/index.en")
    forAllFiles("Donnees/DE/de", "Donnees/extracted/index.de")
  else :
    #align fr-de
    align("fr", "de")
    #align fr-en align("fr", "en")
    #align de-en align("de", "en")
    
  
  

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
from operator import itemgetter
from collections import defaultdict

d_hapax = {} # dict<en|fr|de, dict<filename, list of hapax> >
d_hapax["en"] = {}
d_hapax["fr"] = {}
d_hapax["subfr1"] = {}
d_hapax["subfr2"] = {}
d_hapax["test"] = {}
d_hapax["de"] = {}

index_path = "Donnees/extracted/"

#-------------------------------------------
# LOAD INDEX

def loadIndex(d_hapax, lang) :
# Lit l'index d'une langue donnée pour c
  global index_path
  index_file = index_path + "index." + lang
  with open(index_file, "r") as f:
    for line in f.readlines():
      loadIndexLine(d_hapax[lang], line)


def loadIndexLine(dico, index_line):
  tmp = index_line.split("\t")
  #print tmp[0], " -- ", len(tmp)
  #print ";" in tmp[1]
  #if tmp[0] == ";":
  #	pop tmp[0]
  ##print len(tmp) ####
  dico[tmp[0]] = tmp[1].split(";")


#-------------------------------------------
# CREATE INDEX

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
        
        
#------------------------------------------
# FIND MATCHES

def intersec(x, y) :
	return len(set(x) & set(y))


def normalizedIntersec(x, y) :
	s_x = set(x)
	s_y = set(y)
	return len(s_x & s_y)/len(s_x | s_y)

      
def align(lsrc, ltrgt) :
  """ Write a result file """
  global d_hapax
  global output_file_name
  TOP = 20
  # create (filename, [hapaxes]) (separate function)
  print "Loading indexes..."
  loadIndex(d_hapax, lsrc)
  loadIndex(d_hapax, ltrgt)
  print "Done."
  print "Computing similarities..."
  align_nb = 0 #####
  with open(output_file_name, "w") as output_f:
    for file_src in d_hapax[lsrc].keys() :
      #top20 = None #list of the nearest files
      # compute similarity between hapaxes lists (separate function)
      # memorize in dictionnary of lists the 5 best ones

      #1. baseline
      # list_hapax_source_file, dict<file_name_trgt, list_hapax>, how_many_candidates, similarity_function
      
      top20 = findCandidateScores(d_hapax[lsrc][file_src], d_hapax[ltrgt], TOP, intersec) #TODO
      align_nb += top20.nb_align() #####
      
      
      
      print file_src
      output_f.write(file_src)
      output_f.write(" ### ")
      output_f.write(top20.formatted_output())
      output_f.write("\n")
      #print top20.formatted_output()
      #print top20

    print "Done."
    print "Average number of alignements : ", align_nb*1./len(d_hapax[lsrc].keys())
     
   
def findCandidateScores(l_hpx_src, d_hpx_tgt, top, map_simi):
  top_n_candidates = Top()
  for f_hpx_tgt, l_hpx_tgt in d_hpx_tgt.iteritems():
    top_n_candidates.stack(f_hpx_tgt, map_simi(l_hpx_src, l_hpx_tgt))
  return top_n_candidates
	
	
def find_min(top_n_candidates):
	return min(top_n_candidates, key=top_n_candidates.get)
	
	
# ------------------------------------------

def printResult(fil, top) :
  with open(fil, "r") as f:
    for i in range(top):
      print f.readline()      
  
#-------------------------------------------


class Top:

  def __init__(self):
	  self.list_len = False # sert à vérifier si la liste de 5 éléments contient bien 5 éléments
	  self.list20 = []
		
  def stack(self, elem, score):
    if self.list_len:
      if score > self.list20[19][1]: # if score better than the worst of 5
        self.list20.append((elem, score))
        self.list20.sort(key=itemgetter(1), reverse=True)
        self.list20.pop(20)
    else:
      self.list20.append((elem, score))
      self.list20.sort(key=itemgetter(1), reverse=True)
      if len(self.list20) >= 20:
      	self.list_len = True
      	
  def __str__(self):
    str_rep = ""
    for elem in self.list20:
      str_rep += "  " + elem[0] + " --- " + str(elem[1]) + "\n"
    return str_rep
  
  def formatted_output(self):
    str_rep = ""
    for elem in self.list20:
      str_rep += elem[0] + " "
    return str_rep[:-1]
    
  def nb_align(self):
    return len(self.list20)
     
"""     
class Top:

  def __init__(self):
	  self.list_max = 0
	  self.list = []
		
  def stack(self, elem, score):
  	if score == self.list_max:
  		self.list.append(elem)
  	elif score > self.list_max:
  		self.list = [elem]
  		self.list_max = score
  	
  def __str__(self):
    str_rep = ""
    for elem in self.list:
      str_rep += "  " + elem + " --- " + str(self.list_max) + "\n"
    return str_rep
  
  def nb_align(self):
    return len(self.list)
"""   
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
      

if __name__ == "__main__":
  shouldIndex = False
  if shouldIndex :
    forAllFiles("Donnees/FR/fr", "Donnees/extracted/index.fr")
    forAllFiles("Donnees/EN/en", "Donnees/extracted/index.en")
    forAllFiles("Donnees/DE/de", "Donnees/extracted/index.de")
  
  output_file_name = "top20_fr-en.txt"
  if len(sys.argv) == 4:
    output_file_name = sys.argv[3]

  align("subfr1", "subfr2")

    
  
  

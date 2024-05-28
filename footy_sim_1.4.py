#%%
#-----------------------------------------------------
#--------------------Do zrobienia---------------------
#-----------------------------------------------------

# Ustalić, jakie rzeczy chcę w bazie danych
# Dodać opcje ustalenia wyników konkretnych meczy (żeby wraz z sezonem symulator też miał sens)
# Intefejs
# Możliwość "edycji elo" wg uznania
# Uwzględnić gole
# Dodać do baz danych inne ligi
# MOŻE skorzystać z API ClubElo 
# (Naprawić)? Zamykanie programu
# Wyszukiwanie w bazie danych konkretnych rzeczy (np drużyna x na y miejscu itd.)
# Dodać do tego puchar polski
# Pomyśleć nad kolejnymi dodatkami

#-----------------------------------------------------
#--------------------Przemyślenia---------------------
#-----------------------------------------------------

# Można byłoby dodać formę10 i formę 15, ale spowolniłoby to program
# Gdyby podzielić program na kilka modułów, wydaje mi się, że znacznie przyspieszyłoby to obliczenia

#------------------------------------------------------
#--------------------Biblioteki------------------------
#------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
import statistics as stat
import os as os
import timeit
import pyodbc
import sys

#-----------------------------------------------------
#---------------------Stałe---------------------------
#-----------------------------------------------------

K=30 #Współczynnik aktualizowania elo
SIMS=10000 #liczba symulacji
LEAGUE_SIZE=18 #liczba drużyn
DRAW_CONST=1.2 #współczynnik remisów - użyty do zwiększenia/zmniejszenia szansy na remis, podstawowo jest 2
KLUB_TAB=[] #Tabela, ze wszystkimi drużynami, potrzebna do indeksowania

#----------------------------------------------------
#------------------Opcje-----------------------------
#----------------------------------------------------

MAKE_GRAPHS=False #Czy zapisywać wykresy
GRAPH_COUNT=3 #Ile wykresów zrobić 
PLOT_ELO=False #Czy na wykresie ma być elo
PLOT_PTS=False #Czy na wykresie mają być punkty

DELETE_DATA=False #Tryb TYLKO usuwania danych
CALCULATE=True #Czy generować dane
SAVE_DATA=False #Czy zapisać dane w bazie

HFA_TOGGLE=True  #Czy gospodarz ma posiadać przewagę
FORM5_TOGGLE=True #Czy brać pod uwagę formę z ostatnich 5 meczy
FORM5_VAL=150 #Jaki ma być zakres zmian efektywnego elo
BOOTSTRAP_TOGGLE=True #Czy elo na początku sezonu ma być losowo zmienione
BOOTSTRAP_VAL=50 #Jaki ma być zakres zmian elo
CREATE_SCHEDULE=True #Czy tworzyć terminarz, na razie nie ma innej opcji, trzeba
# byłoby przepisać terminarz do bazy danych, a to zajęło by mi za dużo czasu, innej opcji nie widzę

#----------------------------------------------------
#-----------------Baza Danych------------------------
#----------------------------------------------------

CONN = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\Admin\Desktop\studia\III rok\Sem 6\Wprowadzenie do Pythona\BazaPython.accdb;')
CURSOR = CONN.cursor()

#-----------------------------------------------------
#--------Obliczanie czasu egzakucji programu----------
#-----------------------------------------------------

start = timeit.default_timer()

#-----------------------------------------------------
#---------------------Funkcje------------------------
#-----------------------------------------------------

def DrawOdds(Klub_1,Klub_2):
  return np.exp(-0.5*((
    Klub_1.elo+Klub_1.hfa*HFA_TOGGLE-Klub_2.elo + (Klub_1.form-Klub_2.form)
    )/(200*DRAW_CONST))**2)  /   (np.sqrt(2*np.pi) * DRAW_CONST)

def WinOdds(Klub_1,Klub_2):
  return (1 + 10**(-(
    Klub_1.elo+Klub_1.hfa*HFA_TOGGLE-Klub_2.elo
    )/400))**(-1) - DrawOdds(Klub_1,Klub_2)/2

def LossOdds(Klub_1,Klub_2):
  return 1 - DrawOdds(Klub_1,Klub_2) - WinOdds(Klub_1,Klub_2)

def DrawElo(Klub_1,Klub_2):
  return K*(1/2-(1 + 10**(-(Klub_1.elo-Klub_2.elo)/400))**(-1)) 

def WinElo(Klub_1,Klub_2):
  return K*(1- (1 + 10**(-(Klub_1.elo-Klub_2.elo)/400))**(-1))

def Match_Sim(Klub_1,Klub_2):
  rng=np.random.uniform()
  
  if (rng <= WinOdds(Klub_1,Klub_2)):

    Klub_1.update(Klub_2,"Win")
    Klub_2.update(Klub_1,"Loss")

  elif (rng <= WinOdds(Klub_1,Klub_2)+DrawOdds(Klub_1,Klub_2)):
    
    Klub_1.update(Klub_2,"Draw")
    Klub_2.update(Klub_1,"Draw")

  else:

    Klub_1.update(Klub_2,"Loss")
    Klub_2.update(Klub_1,"Win")
  
  Klub_1.hist_elo.append(Klub_1.elo)
  Klub_2.hist_elo.append(Klub_2.elo)
  Klub_1.hist_pts.append(Klub_1.pts)
  Klub_2.hist_pts.append(Klub_2.pts)   

#-----------------------------------------------------

def Create_Schedule(size):

  sched=[]
  temp_tab=[]
  for i in range(1,size):
    
    temp_tab.append(i+1) #tabela posiadająca liczby od 2 do 18, potrzebna ze względu na algorytm tworzenia terminarza

  for i in range(1,size): #kolejki pierwszej rundy
    
    rnd=[[1,temp_tab[-i]]]
    
    for j in range(1,int(size/2+1)):
      
      rnd.append([temp_tab[j-i],temp_tab[size-j-i-1]])

    sched.append(rnd)
  
  for i in range(0,size-1): #kolejki rundy rewanżowej, to poprostu kolejki pierwszej rundy ale z zamienionymi miejscami drużyn
    
    rnd=[]

    for j in range(0,int(size/2)-1):

      rnd.append([sched[i][j][1],sched[i][j][0]])
    
    sched.append(rnd)

  return sched

#-----------------------------------------------------

def Short_Sort():
  
  for i in range(1,LEAGUE_SIZE):
    
    for j in range(0,LEAGUE_SIZE-i):

      if KLUB_TAB[j].pts<KLUB_TAB[j+1].pts:

        temp_val=KLUB_TAB[j+1]
        KLUB_TAB[j+1]=KLUB_TAB[j]
        KLUB_TAB[j]=temp_val
    
  for i in range(1,LEAGUE_SIZE+1):
    KLUB_TAB[-i].stand=LEAGUE_SIZE+1-i

def Long_Sort():

  for i in range(1,LEAGUE_SIZE):
    
    for j in range(0,LEAGUE_SIZE-i):

      if KLUB_TAB[j].stand_sum>KLUB_TAB[j+1].stand_sum:

        temp_val=KLUB_TAB[j+1]
        KLUB_TAB[j+1]=KLUB_TAB[j]
        KLUB_TAB[j]=temp_val


#-----------------------------------------------------

def Table():

  Long_Sort()

  print('AVG PLACE |  EXPTS  |   1st   |   Top3   |   Top4   |  RELEG  |  NAME ')

  for element in KLUB_TAB:

    print(element.stand_sum/SIMS, ' | ', element.pts_sum/SIMS, ' | ', element.champ/SIMS,  ' | '
        , element.top3/SIMS, ' | ', element.top4/SIMS, ' | ', element.releg/SIMS, ' | '
        , element.name)

#-----------------------------------------------------
def Plot_Elo(i):
  plot=plt.figure(figsize=(15,10))
  for element in KLUB_TAB:
    plt.plot(range(1,2*LEAGUE_SIZE-1),element.hist_elo,color=element.color,label=element.name)
  plt.ylabel('Total Elo')
  plt.xlabel('Round')
  plt.legend(loc='upper center',ncol=6,bbox_to_anchor=(0.5, 1.1))
  plt.savefig('wykres'+str(i))

def Plot_Pts(i):
  plt.figure(figsize=(15,10))
  for element in KLUB_TAB:
    plt.plot(range(1,2*LEAGUE_SIZE-1),element.hist_pts,color=element.color,label=element.name)
  plt.ylabel('Total Points')
  plt.xlabel('Round')
  plt.legend(loc='upper center',ncol=6,bbox_to_anchor=(0.5, 1.1))
  plt.savefig('wykres'+str(i))

def Double_Plot(i):

  dp,(axis1,axis2)=plt.subplots(2,1,sharex=True,figsize=(15,10))
  axis1.set_ylabel('Total Points')
  axis2.set_ylabel('Total Elo')
  axis2.set_xlabel('Round')
  
  for element in KLUB_TAB:
    axis1.plot(range(1,2*LEAGUE_SIZE-1),element.hist_pts,color=element.color,label=element.name)
    axis2.plot(range(1,2*LEAGUE_SIZE-1),element.hist_elo,color=element.color,label=element.name)
  
  axis1.legend(loc='upper center',ncol=6,bbox_to_anchor=(0.5, 1.20))
  plt.savefig('wykres'+str(i))
  
def Run_Sim():  
  
  for i in range(0,SIMS):       #Symulacja MonteCarlo wielu sezonów

    for Match_Week in SCHEDULE: #Symulacja jednego sezonu
  
      for Match in Match_Week:  #Symulacja jednej kolejki
    
        Klub_Temp=[]
    
        for Team in Match:      #Symulacja jednego meczu
      
          Klub_Temp.append(KLUB_TAB[Team-1])    

        Match_Sim(Klub_Temp[0],Klub_Temp[1])

    Short_Sort()

    if MAKE_GRAPHS and GRAPH_COUNT>i:
      
      if PLOT_ELO and PLOT_PTS:
        Double_Plot(i)

      elif PLOT_ELO:
        Plot_Elo(i)
      
      elif PLOT_PTS:
        Plot_Pts(i)
    
    
    
    if SAVE_DATA:
      table_create_querry='CREATE TABLE Sezon'+str(i+1)+'''(
        [id] INT PRIMARY KEY,
        [nazwa] CHAR(255),
        [punkty] INT,
        [miejsce] INT,
        [bootstrap] FLOAT
      )'''
      CURSOR.execute(table_create_querry)
      k=1
    
    for element in KLUB_TAB:
      if SAVE_DATA:
        Data_Save(element,i+1,k)
        k+=1
      element.season_summary()
      
#----------------------------------------------------------

def Load_DB():
  
  CURSOR.execute('SELECT * FROM Klub_Input_Eks')   
  for row in CURSOR.fetchall():
    Temp=Klub(row[1],row[2],row[3],50,0)
    KLUB_TAB.append(Temp)

#----------------------------------------------------------

def Delete():
  i=1
  while True:
    try:
      CURSOR.execute('DROP TABLE Sezon'+str(i))
      print(i)
      i+=1
    except:
      print("usunięto wszystkie dane")
      CONN.commit()
      CURSOR.close()
      CONN.close()
      os._exit(1)
#----------------------------------------------------------

def Data_Save(Klub,sezon,id):
  insert_query= 'INSERT INTO Sezon'+str(sezon)+''' (id, nazwa, punkty, miejsce, bootstrap)
    VALUES (?, ?, ?, ?, ?)
  '''
  data=(id,Klub.name,Klub.pts,Klub.stand,Klub.bootstrap)
  CURSOR.execute(insert_query,data)
  CONN.commit()


#----------------------------------------------------------
#----------------------Klasa-------------------------------
#----------------------------------------------------------

class Klub(object):

  def __init__(self, elo, nazwa, kolor, przewaga, punkty):
    self.elo = elo  #elo w sezonie
    self.elo_const = elo #elo od którego drużyna zazcyna każdy sezon
    self.pts = punkty  #punkty w sezonie
    self.pts_sum = 0 #suma punktów w sezonie
    self.hfa = przewaga #przewaga podczas gry w domu (eng. home field advantage)
    self.name = nazwa
    self.color = kolor 
    self.form = 0
    self.draws = 0
    self.loses = 0
    self.wins = 0
    self.bootstrap = 0 
    self.stand = 0
    self.stand_sum = 0 #suma miejsc na których drużyna skończyła miejsce (do średniej)
    self.champ = 0
    self.top3 = 0
    self.top4 = 0
    self.releg = 0

    self.hist_elo = [] #rozkład elo w jednym sezonie
    self.hist_pts = [] #rozkład pkt w jednym sezonie

  def update(self,oponent,result):
    if result == "Win":
      self.elo += WinElo(self,oponent)
      self.pts += 3 
      self.wins += 1
    
    elif result == "Draw":
      self.elo += DrawElo(self,oponent)
      self.pts += 1
      self.draws += 1

    elif result == "Loss":
      self.elo -= WinElo(oponent,self)  #odwrotnie podanie klubów daje Loss Elo
      self.loses += 1
    else:
      "Błąd w programie."
    
    if FORM5_TOGGLE:
      
      if len(self.hist_pts)>5:
        self.form = (self.hist_pts[-1] - self.hist_pts[-6])*FORM5_VAL/15

      if len(self.hist_pts) == 0:
        self.form  = 0

      else:
        self.form = (self.hist_pts[-1] - self.hist_pts[0])*FORM5_VAL/(3*len(self.hist_pts))

  def reset(self):
    
    self.bootstrap = 2*BOOTSTRAP_TOGGLE*BOOTSTRAP_VAL*(np.random.uniform()-0.5)
    self.elo = self.elo_const
    self.wins = 0
    self.draws = 0
    self.loses = 0
    self.pts_sum += self.pts
    self.pts = 0
    self.hist_pts = []
    self.hist_elo = []
  
  def plot_elo(self): #plot elo
    plt.plot(range(1,2*LEAGUE_SIZE-1),self.hist_elo,color=self.color,label=self.name) #pamiętać, że tutaj jest do zmiany zawsze ilość meczy

  def plot_elo1(self): #plot pts ale nie chce mi się zmieniać komend na dole xd
    plt.plot(range(1,2*LEAGUE_SIZE-1),self.hist_pts,color=self.color,label=self.name) #pamiętać, że tutaj jest do zmiany zawsze ilość meczy

  def print(self):
    print(self.name, self.pts)
    
  def season_summary(self):

    if self.stand == 1:
      self.champ+=1
      self.top3+=1
      self.top4+=1
    elif self.stand == 2 or self.stand == 3:
      self.top3+=1 
      self.top4+=1
    elif self.stand == 4:
      self.top4+=1
    elif self.stand == 16 or self.stand == 17 or self.stand == 18:
      self.releg+=1
    
    self.stand_sum+=self.stand
    self.stand=0
    self.reset()
#-----------------------------------------------------
#--------------------------Program--------------------
#-----------------------------------------------------

if DELETE_DATA:
  Delete()

Load_DB()

if CREATE_SCHEDULE:
  SCHEDULE = Create_Schedule(LEAGUE_SIZE)

if CALCULATE:
  Run_Sim()
  Table()

print("Policzone dla: K = ", K, "DRAW_CONST = ",DRAW_CONST, "SIMS = ",SIMS,
       "BOOTSTRAP_VAL = ", BOOTSTRAP_VAL*BOOTSTRAP_TOGGLE, "HFA = ", HFA_TOGGLE )

finish = timeit.default_timer()

print("Time:",finish-start)

CURSOR.close()
CONN.close()
#--------------------------------------------------
#-----------------BACKUP CODE----------------------
#--------------------------------------------------

# Klub1 = Klub(1557,0,0,"Lech Poznań","#6bd2db")
# KLUB_TAB.append(Klub1)
# Klub2 = Klub(1275,0,0,"Puszcza Niepołomice","#a0d6b4")
# KLUB_TAB.append(Klub2)
# Klub3 = Klub(1352,0,0,"Zagłębie Lubin","#f37735")
# KLUB_TAB.append(Klub3)
# Klub4 = Klub(1325,0,0,"Stal Mielec","#999999")
# KLUB_TAB.append(Klub4)
# Klub5 = Klub(1478,0,0,"Legia Warszawa","#2a623d")
# KLUB_TAB.append(Klub5)
# Klub6 = Klub(1544,0,0,"Raków Częstochowa", "#673888")
# KLUB_TAB.append(Klub6)
# Klub7 = Klub(1353,0,0,"Jagiellonia Białystok","#ffcf40")
# KLUB_TAB.append(Klub7)
# Klub8 = Klub(1275,0,0,"Ruch Chorzów","#005b96")
# KLUB_TAB.append(Klub8)
# Klub9 = Klub(1459,0,0,"Pogoń Szczecin","#602320")
# KLUB_TAB.append(Klub9)
# Klub10 = Klub(1391,0,0,"Górnik Zabrze","#dabcff")
# KLUB_TAB.append(Klub10)
# Klub11 = Klub(1449,0,0,"Piast Gliwice","#ff9e99")
# KLUB_TAB.append(Klub11)
# Klub12 = Klub(1379,0,0,"Cracovia","#d9534f")
# KLUB_TAB.append(Klub12)
# Klub13 = Klub(1366,0,0,"Warta Poznań","#00b159")
# KLUB_TAB.append(Klub13)
# Klub14 = Klub(1345,0,0,"Radomiak Radom","#007777")
# KLUB_TAB.append(Klub14)
# Klub15 = Klub(1314,0,0,"Korona Kielce","#eeba30")
# KLUB_TAB.append(Klub15)
# Klub16 = Klub(1310,0,0,"Śląsk Wrocław","#ddfffc")
# KLUB_TAB.append(Klub16)
# Klub17 = Klub(1276,0,0,"Widzew Łódź","#d29985")
# KLUB_TAB.append(Klub17)
# Klub18 = Klub(1275,0,0,"ŁKS Łódź","#ce4a4a")
# KLUB_TAB.append(Klub18)
#%%

#%%
#-----------------------------------------------------
#--------------------Do zrobienia---------------------
#-----------------------------------------------------
# Uwzględnić kto jest gospodarzem w obliczaniu szans
# Zintegrować z bazą danych
# Ustalić, co chcę w bazie danych

# COŚ SIĘ ŹLE LICZY!!!!!!!!!!!! 

#------------------------------------------------------
#--------------------Biblioteki------------------------
#------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import statistics as stat
import os as os
import timeit
#-----------------------------------------------------
#---------------------Stałe---------------------------
#-----------------------------------------------------

K=30 #Współczynnik aktualizowania elo
SIMS=1000 #liczba symulacji
LEAGUE_SIZE=18 #liczba drużyn
DRAW_CONST=1.2 #współczynnik remisów - użyty do zwiększenia/zmniejszenia szansy na remis, podstawowo jest 2
MODE=1 #Tryb programu, 
#mode 1 --> symuluje x razy i tworzy x wykresów
#mode 2 --> symuluje x razy i liczy średnia statystyki
#-----------------------------------------------------
#--------Obliczanie czasu egzakucji programu----------
#-----------------------------------------------------

start = timeit.default_timer()

#-----------------------------------------------------
#---------------------Funkcje------------------------
#-----------------------------------------------------

def DrawOdds(Klub_1,Klub_2):
  return np.exp(-0.5*((Klub_1.elo-Klub_2.elo)/(200*DRAW_CONST))**2)  /   (np.sqrt(2*np.pi) * DRAW_CONST)

def WinOdds(Klub_1,Klub_2):
  return (1 + 10**(-(Klub_1.elo-Klub_2.elo)/400))**(-1) - DrawOdds(Klub_1,Klub_2)/2

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

def Table(Tab):

  points=[]
  names=[]
  draws=[]
  wins=[]
  loses=[]

  for element in Tab:
    
    names.append(element.name)
    points.append(element.pts)
    draws.append(element.draws)
    wins.append(element.wins)
    loses.append(element.loses)

  print('Pts| Name')
  for i in range(1,LEAGUE_SIZE): #muszę zdecydować czy trzymać to w bazie danych, póki co drukuję

    for j in range(0,LEAGUE_SIZE-i):

      if points[j]>points[j+1]:

        Temp_val=points[j+1]
        points[j+1]=points[j]
        points[j]=Temp_val

        Temp_val=names[j+1]
        names[j+1]=names[j]
        names[j]=Temp_val

        Temp_val=draws[j+1]
        draws[j+1]=draws[j]
        draws[j]=Temp_val

        Temp_val=wins[j+1]
        wins[j+1]=wins[j]
        wins[j]=Temp_val

        Temp_val=loses[j+1]
        loses[j+1]=loses[j]
        loses[j]=Temp_val
  
  for i in range(1,LEAGUE_SIZE+1):

    print(points[-i]/SIMS,"|",names[-i])


#-----------------------------------------------------

def Double_Plot():

  dp,(axis1,axis2)=plt.subplots(2,1,sharex=True,figsize=(15,10))
  axis1.set_ylabel('Total Points')
  axis2.set_ylabel('Total Elo')
  axis2.set_xlabel('Round')
  
  for element in KLUB_TAB:
    axis1.plot(range(1,2*LEAGUE_SIZE-1),element.hist_pts,color=element.color,label=element.name)
    axis2.plot(range(1,2*LEAGUE_SIZE-1),element.hist_elo,color=element.color,label=element.name)
  
  axis1.legend(loc='upper center',ncol=6,bbox_to_anchor=(0.5, 1.20))

def Run_Sim(sim_number):  
  
  for i in range(0,sim_number):       #Symulacja MonteCarlo wielu sezonów

    for Match_Week in SCHEDULE: #Symulacja jednego sezonu
  
      for Match in Match_Week:  #Symulacja jednej kolejki
    
        Klub_Temp=[]
    
        for Team in Match:      #Symulacja jednego meczu
      
          Klub_Temp.append(KLUB_TAB[Team-1])    

        Match_Sim(Klub_Temp[0],Klub_Temp[1])

  
    for element in KLUB_TAB:
      element.reset()
    
  

#----------------------------------------------------------
#----------------------Klasa-------------------------------
#----------------------------------------------------------

class Klub(object):

  def __init__(self, elo, punkty, przewaga, nazwa, kolor):
    self.elo = elo  #elo w sezonie
    self.elo_const = elo #elo od którego drużyna zazcyna każdy sezon
    self.pts = punkty  #punkty w sezonie
    self.hfa = przewaga #przewaga podczas gry w domu (eng. home field advantage)
    self.name = nazwa
    self.color = kolor 
    self.draws = 0
    self.loses = 0
    self.wins = 0

    self.finish = [] #zbiór miejsc, na których drużyna skończyła sezon
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

  def reset(self):
    self.elo = self.elo_const
    #self.wins = 0
    #self.draws = 0
    #self.loses = 0
  
  def plot_elo(self): #plot elo
    plt.plot(range(1,2*LEAGUE_SIZE-1),self.hist_elo,color=self.color,label=self.name) #pamiętać, że tutaj jest do zmiany zawsze ilość meczy

  def plot_elo1(self): #plot pts ale nie chce mi się zmieniać komend na dole xd
    plt.plot(range(1,2*LEAGUE_SIZE-1),self.hist_pts,color=self.color,label=self.name) #pamiętać, że tutaj jest do zmiany zawsze ilość meczy

  def print(self):
    print(self.name, self.pts)
    


#-----------------------------------------------------
#--------------------------Program--------------------
#-----------------------------------------------------
   

#import mysql.connector as sql

#database = sql.connect(
#  user="name",
#  password="123"
#)
#cursor=database.cursor()
#cursor.execute("CREATE DATABASE mydatabase")
#Drużyny = ('Cracovia', 'Górnik Zabrze', 'Jagiellonia Białystok', 'Korona Kielce', 'Lech Poznań',\
#          'Legia Warszawa', 'ŁKS Łódź', 'Piast Gliwice', 'Pogoń Szczecin', 'Puszcza Niepołomice',\
#          'Radomiak Radom', 'Raków Częstochowa', 'Ruch Chorzów', 'Stal Mielec', 'Śląsk Wrocław', \
#          'Warta Poznań', 'Widzew Łódź', 'Zagłębie Lubin')

#Punktacja = {}
#for element in Drużyny:
#  Punktacja[element] = 0

#Elo = {'Lech Poznań':	1557,
#  'Raków Częstochowa':	1544,
#  'Legia Warszawa':	1478,
#  'Pogoń Szczecin':	1459,
#  'Piast Gliwice':	1449,
#  'Górnik Zabrze':	1391,
#  'Cracovia':	1379,
#  'Warta Poznań':	1366,
#  'Jagiellonia Białystok':	1353,
#  'Zagłębie Lubin': 1352,
#  'Radomiak Radom':	1345,
#  'Stal Mielec':	1325,
#  'Korona Kielce': 1314,
#  'Śląsk Wrocław':	1310,
#  'Widzew Łódź':	1276,
#  'ŁKS Łódź':	1275,
#  'Puszcza Niepołomice':	1275,
#  'Ruch Chorzów' : 1275}

#def __init__(self, elo, terminarz, punkty, przewaga, nazwa):

KLUB_TAB=[] #Tabela, ze wszystkimi drużynami, potrzebna do indeksowania

Klub1 = Klub(1557,0,0,"Lech Poznań","#6bd2db")
KLUB_TAB.append(Klub1)
Klub2 = Klub(1275,0,0,"Puszcza Niepołomice","#a0d6b4")
KLUB_TAB.append(Klub2)
Klub3 = Klub(1352,0,0,"Zagłębie Lubin","#f37735")
KLUB_TAB.append(Klub3)
Klub4 = Klub(1325,0,0,"Stal Mielec","#999999")
KLUB_TAB.append(Klub4)
Klub5 = Klub(1478,0,0,"Legia Warszawa","#2a623d")
KLUB_TAB.append(Klub5)
Klub6 = Klub(1544,0,0,"Raków Częstochowa", "#673888")
KLUB_TAB.append(Klub6)
Klub7 = Klub(1353,0,0,"Jagiellonia Białystok","#ffcf40")
KLUB_TAB.append(Klub7)
Klub8 = Klub(1275,0,0,"Ruch Chorzów","#005b96")
KLUB_TAB.append(Klub8)
Klub9 = Klub(1459,0,0,"Pogoń Szczecin","#602320")
KLUB_TAB.append(Klub9)
Klub10 = Klub(1391,0,0,"Górnik Zabrze","#dabcff")
KLUB_TAB.append(Klub10)
Klub11 = Klub(1449,0,0,"Piast Gliwice","#ff9e99")
KLUB_TAB.append(Klub11)
Klub12 = Klub(1379,0,0,"Cracovia","#d9534f")
KLUB_TAB.append(Klub12)
Klub13 = Klub(1366,0,0,"Warta Poznań","#00b159")
KLUB_TAB.append(Klub13)
Klub14 = Klub(1345,0,0,"Radomiak Radom","#007777")
KLUB_TAB.append(Klub14)
Klub15 = Klub(1314,0,0,"Korona Kielce","#eeba30")
KLUB_TAB.append(Klub15)
Klub16 = Klub(1310,0,0,"Śląsk Wrocław","#ddfffc")
KLUB_TAB.append(Klub16)
Klub17 = Klub(1276,0,0,"Widzew Łódź","#d29985")
KLUB_TAB.append(Klub17)
Klub18 = Klub(1275,0,0,"ŁKS Łódź","#ce4a4a")
KLUB_TAB.append(Klub18)



SCHEDULE = Create_Schedule(LEAGUE_SIZE)


#Run_Sim()


#Table(KLUB_TAB)
#print("Policzone dla: K = ", K, "DRAW_CONST = ", DRAW_CONST, "SIMS = ",SIMS)

finish = timeit.default_timer()

print("Time:",finish-start)
#%%

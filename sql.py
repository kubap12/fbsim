#%%

#delete_querry = "DELETE FROM Klub_Input_Eks" ----> Usuwa całą tabelę
#cursor.execute(delete_querry)



import os
import pyodbc

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\Admin\Desktop\studia\III rok\Sem 6\Wprowadzenie do Pythona\BazaPython.accdb;')
# ^--------- stworzenie połączenia

cursor = conn.cursor() # ------> stworzenie kursora

cursor.execute('SELECT * FROM Klub_Input_Eks')  

for row in cursor.fetchall():
    print(row)

insert_query = "INSERT INTO Klub_Input_Eks (id,elo,nazwa,kolor) VALUES (?,?,?,?)"
data_to_input = ()
cursor.execute(insert_query, data_to_input)



conn.commit()   # ------> zapisanie bazy danych
cursor.close()  # ------> zamknięcie kursora
conn.close      # ------> zamknięcie połączenia
# %%

import sqlite3
import json
import csv
import smtplib
import sys
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from models.Databases import *
from models.Owner import *
from models.Manager import *



data = {}
data['db_list'] = []
owner_db_list = OwnerList()
managers_db_list = ManagerList()
db_list = DBlist()

# connection = sqlite3.connect("administration_db")
# cursor = connection.cursor()



class GUI():

    def __init__(self, window):

        self.window = window
        self.window.title('Revalida de Base de Datos')
        self.window.config(background="black")

        #Contenedor
        frame = LabelFrame(self.window)
        frame.grid(row = 0, column = 0 , columnspan = 3 , pady = 1, sticky = 'E'+'W')
        frame.config(background = "black")

        #Botones
        ttk.Button(frame,text = "Conectar BBDD", command = initializateDB).grid(pady = 7,padx = 1, columnspan = 3, sticky = 'E'+'W')
        ttk.Button(frame,text = "Importar CSV", command = loadCsv).grid(pady = 7,columnspan = 3,padx = 1,  sticky = 'E'+'W')
        ttk.Button(frame,text = "Importar JSON", command = loadJson).grid(pady = 7,padx = 1, columnspan = 3, sticky = 'E'+'W')
        ttk.Button(frame,text = "Solicitar confirmacion", command = searchCriticalDB).grid(pady = 7,padx = 1, columnspan = 3, sticky = 'E'+'W')
        ttk.Button(frame,text = "SALIR", command = exit).grid( pady = 7,padx = 1, columnspan = 3, sticky = 'E'+'W')

        #tabla
        self.tree = ttk.Treeview(height = 9 , columns = ('#0','#1','#2'))
        self.tree.grid(pady=18, padx = 12, row = 0, column = 3)
        self.tree.heading('#0', text = 'Name', anchor = CENTER)
        self.tree.heading('#1', text = 'Manager', anchor = CENTER)
        self.tree.heading('#2', text = 'Owner', anchor = CENTER)
        self.tree.heading('#3', text = 'Classification', anchor = CENTER)
        self.tree.column('#0', width = 150, stretch = False)
        self.tree.column('#1', width = 150, stretch = False)
        self.tree.column('#2', width = 150, stretch = False)
        self.tree.column('#3', width = 150, stretch = False)



# ******************** FUNCIONES - BASE DE DATOS ******************************



# Inicializo la Base de Datos
def initializateDB():

    connection = sqlite3.connect("administration_db")
    cursor = connection.cursor()

    try:

        cursor.execute('''
        CREATE TABLE OWNERS (
        OWNER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        OWNER_NAME VARCHAR(50) NOT NULL,
        OWNER_LASTNAME VARCHAR(50) NOT NULL,
        OWNER_USERNAME VARCHAR(50) ,
        OWNER_EMAIL VARCHAR(50) NOT NULL,
        OWNER_TIME_STAMP VARCHAR(50))
        ''')

        cursor.execute('''
        CREATE TABLE MANAGERS (
        MANAGER_ID INTEGER PRIMARY KEY NOT NULL,
        MANAGER_USERNAME VARCHAR(50),
        MANAGER_STATE VARCHAR(50),
        MANAGER_EMAIL VARCHAR(50) NOT NULL)
        ''')

        cursor.execute('''
        CREATE TABLE DATABASES (
        DATABASE_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        MANAGER_ID INTEGER,
        OWNER_ID INTEGER,
        CONFIDENTIALITY VARCHAR(50) NOT NULL,
        INTEGRITY VARCHAR(50) NOT NULL,
        AVAILABILITY VARCHAR(50) NOT NULL,
        NAME VARCHAR(50) UNIQUE,
        FINAL_CLASSIFICATION VARCHAR(50))
        ''')

        connection.commit()
        messagebox.showinfo("BBDD","La base de datos fue inicializada correctamente.")
        connection.close()

    except Exception as e:

         messagebox.showerror("Atencion!","La base de datos ya fue creada !!")

# Inserto un nuevo Owner
def insertOwner(name,lastname,username,email,time_stamp):

    connection = sqlite3.connect("administration_db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO OWNERS VALUES (NULL,?,?,?,?,?)",(name,lastname,username,email,time_stamp))
    connection.commit()
    id = cursor.lastrowid
    connection.close()
    print ("\nSe ha ingresado correctamente un nuevo Owner")

    return id

# Inserto un nuevo Manager
def insertManager(manager_id,username,state,email):

    connection = sqlite3.connect("administration_db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO MANAGERS VALUES (?,?,?,?)",(manager_id,username,state,email))
    connection.commit()
    connection.close()
    print ("\nSe ha ingresado correctamente un nuevo Manager")

# Inserto una nueva Base de Datos
def insertDatabase(manager_id,owner_id,confidentiality,integrity,availability,name,final_classification):

    try:

        connection = sqlite3.connect("administration_db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO DATABASES VALUES (NULL,?,?,?,?,?,?,?)",(manager_id,owner_id,confidentiality,integrity,availability,name,final_classification))
        connection.commit()
        id = cursor.lastrowid
        connection.close()
        print ("\nBD %s creada exitosamente."%name.upper())

    except :

        connection.close()
        pass

    if id:
        return id



# ********************///*******************************************************



# En base al nombre completo y lo separo en : primer nombre y apellido
def separateName(word):

        name = ''
        lastname = ''
        separator = word.split()

        if len(separator) > 2:

            name = separator[0]
            last_value = separator[-1]
            lastname = last_value

        else:

            name = separator[0]
            lastname = separator[1]

        return name,lastname

# En base al email , obtengo el nombre completo
def separateEmail(email):


    if '@' in email:

        separator = email.split('@')
        complete_name = separator[0]

        if '.' in email:

            separator2 = complete_name.split('.')
            name = separator2[0]
            lastname = separator2[1]
            final_name = name+" "+lastname

    else:

        messagebox.showerror("Error", "Alguno de los emails ingresados sn incorrectos (@/.)")


    return final_name.title()

# En base al nombre creo el email
def createEmail(name,lastname):

        new_email = name+"."+lastname+"@mercadolibre.com"
        return new_email

# Envio email
def sendEmail(owner_name,owner_lastname,manager_email,manager_state,name_db,confidentiality,integrity,availability,final_classification):

    connection = sqlite3.connect("administration_db")
    cursor = connection.cursor()

    if manager_state == "activo":

        manager_name = separateEmail(manager_email)
        SERVER = "smtp.gmail.com"
        PORT = 587
        FROM = "meli.challenge.databases@gmail.com"
        PASSWORD = "verdad8756"
        TO = [manager_email]
        SUBJECT = "Seguridad Informatica : Revalida automatica de Base de Datos"
        MESSAGE_TEXT = ("Estimado/a %s,\n\nNos encontramos realizando el proceso anual de reclasificacion de Base de Datos. En ese sentido, te pedimos por favor nos envies tu conformidad en caso de estar de acuerdo con los datos brindados a continuacion :\
                         \n\n\nBase de datos : %s \
                         \nIntegridad : %s\
                         \nConfidencialidad : %s\
                         \nDisponibilidad : %s\
                         \nClasificacion Final : %s\
                         \nOwner : %s %s \
                         \n\n\nAgradecemos tu respuesta,\
                         \nSaludos cordiales." % (manager_name,name_db.upper(),integrity.upper(),confidentiality.upper(),availability.upper(),final_classification.upper(),owner_name.upper(),owner_lastname.upper()))


        try:


            server = smtplib.SMTP(SERVER,PORT)
            server.starttls()
            server.login(FROM,PASSWORD)
            message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO), SUBJECT, MESSAGE_TEXT)
            server.sendmail(FROM,TO,message)
            server.quit()
            messagebox.showinfo("EMAIL","Se envio el email al Manager %s correctamente"%manager_name)


        except:

            messagebox.showerror("EMAIL","Fallo al enviar el email")

    else:

        messagebox.showerror("EMAIL","No se pudo enviar el email ya que el manager de la base de datos se encuentra inactivo")

# En base al email creo el username
def createUsername2(email):

    separator = email.split('@')
    complete_name = separator[0]

    separator2 = complete_name.split('.')
    name = separator2[0]
    lastname = separator2[1]

    if len(separator2) > 2:

        name = separator[0]
        last_value = separator[-1]
        lastname = last_value

    username = name[0]+lastname

    return username.lower()

# En base al nombre creo el username
def createUsername1(word):

    name = ''
    lastname = ''
    username = ''
    separator = word.split()


    # si tiene mas de dos palabras ..solo me quedo con la primera para el nombre y ultima para apellido
    if len(separator) > 2:

        name = separator[0]
        last_value = separator[-1]
        lastname = last_value

    if len(separator) == 0:

        print ("Se requiere nombre y apellido")


    else:

        name = separator[0]
        lastname = separator[1]

    username = name[0]+lastname

    return username.lower()

# Terminar aplicacion
def exit():

    sys.exit()


# ********************///*******************************************************



# Busco Owner segun username
def searchOwner(username):

    connection = sqlite3.connect("administration_db")
    cursor = connection.cursor()

    bool = False

    cursor.execute("SELECT * FROM OWNERS WHERE OWNER_USERNAME = '%s'" % username)
    result_set = cursor.fetchall()
    connection.commit()
    connection.close()

    if len(result_set) != 0:

        bool = True


    return bool

#Busco Manager segun username
def searchManager(username):


    connection = sqlite3.connect("administration_db")
    cursor = connection.cursor()

    bool = False
    manager_id = 0
    manager_email = ''

    #Cuando el username del owner es igual al username de la tabla manager (que a su vez es el username de su owner)
    cursor.execute("SELECT MANAGER_ID,MANAGER_EMAIL FROM MANAGERS WHERE MANAGER_USERNAME = '%s'" % str(username))
    result_set = cursor.fetchall()
    connection.close()

    if len(result_set) != 0:

        for m in result_set:

            bool = True
            manager_id = m[0]
            manager_email = m[1]
            break


    return bool,manager_id,manager_email

# Envio email a los Managers de las bases criticas
def searchCriticalDB():

    connection = sqlite3.connect("administration_db")
    cursor = connection.cursor()

    try:

        cursor.execute("SELECT O.OWNER_ID, O.OWNER_NAME, O.OWNER_LASTNAME, M.MANAGER_ID, M.MANAGER_EMAIL, M.MANAGER_STATE, D.NAME, D.CONFIDENTIALITY , D.INTEGRITY, D.AVAILABILITY, D.FINAL_CLASSIFICATION \
                        FROM OWNERS O, MANAGERS M, DATABASES D \
                        WHERE O.OWNER_ID = D.OWNER_ID \
                        AND M.MANAGER_ID = D.MANAGER_ID \
                        AND D.FINAL_CLASSIFICATION = 'HIGH'")

        result_set = cursor.fetchall()
        connection.close()

        for i in result_set:

            owner_name = i[1]
            owner_lastname = i[2]
            manager_email = i[4]
            manager_state = i[5]
            name_db = i[6]
            confidentiality = i[7]
            integrity = i[8]
            availability = i[9]
            final_classification = i[10]

            message = messagebox.askquestion("EMAIL", "Desea enviar email de revalida al Manager de la Base de Datos : %s ?"%name_db.upper())

            if message == 'yes':

                sendEmail(owner_name,owner_lastname,manager_email,manager_state,name_db,confidentiality,integrity,availability,final_classification)


    except sqlite3.OperationalError as e:

        messagebox.showerror("Error", "Debe conectar la Base de datos primero")

    except Exception as e:

        messagebox.showwarning("Send Email","No se pudo realizar la consulta a la BBDD")



# *********************** FUNCIONES - CALCULO DE CLASIFICACIONES ***************



# Le asigno al parametro confidentiality un score (0,1 o 2)
def getConfidentiality(c):

    confidentiality = 0

    if c == "medium":

        confidentiality = 1

    if c == "high":

        confidentiality = 2

    return confidentiality

# Le asigno al parametro integrity un score (0,1 o 2)
def getIntegrity(i):

    integrity = 0

    if i == "medium" :

       integrity = 1

    if i == "high" :

       integrity = 2

    return integrity

# Le asigno al parametro availability un score (0,1 o 2)
def getAvailability(a):

    availability = 0

    if a == "medium" :

       availability = 1

    if a == "high" :

       availability = 2

    return availability

# Con los scores obtenidos obtengo la clasificacion final
def calculateClassification(confidentiality,integrity,availability):

    total_score = 0
    final_classification = ''

    condifentiality_score = int(getConfidentiality(confidentiality))
    integrity_score = int(getIntegrity(integrity))
    availability_score = int(getAvailability(availability))

    # Sumo scores
    total_score = condifentiality_score+integrity_score+availability_score

    # si esta entre 0 y 2 es LOW
    if total_score >= 0 and total_score <= 2:

        final_classification = "LOW"

    # Si esta entre 2 y 4 es MEDIUM
    elif total_score > 2 and total_score <= 4:

        final_classification = "MEDIUM"

    # Si es mas de cuatro sera HIGH
    else:

        final_classification = "HIGH"


    return final_classification



# ********************** FUNCIONES - CARGA DE DATOS ****************************



#Validaciones campos
def validateJson(db_name,name,email,username):

    # Si el nombre y el email, son nulos. No se puede ingresar el registro
    if len(name.replace(" ","")) != 0 or len(email.replace(" ","")) != 0:

        # Si el nombre es nulo y email no : creo nombre y username
        if len(name.replace(" ","")) == 0 and len(email.replace(" ","")) != 0 :

            name = separateEmail(email)
            username = createUsername2(email)

        # Si el email es nulo y el nombre no :  creo email y username
        elif len(name.replace(" ","")) != 0 and len(email.replace(" ","")) == 0:

            username = createUsername1(name)
            first_name,lastname = separateName(name)
            email = createEmail(first_name,lastname)

    else:

        messagebox.showwarning("BBDD","BD %s con nombre y email nulos. Complete los datos y vuelva a ingresarla"% db_name.upper())

# Cargo datos de los Managers (.csv)
def loadCsv():


    i = 0


    try:

        with open('user_manager.csv') as csv_userManager:

            csv_read = csv.reader(csv_userManager)

            for manager in csv_read:

                    i += 1
                    insertManager(manager[0],manager[1],manager[2],manager[3])
                    manager_db = Manager(manager[0],manager[1],manager[2],manager[3])
                    managers_db_list.addManager(manager_db)
                    name_manager = separateEmail(manager[3])

            messagebox.showinfo("CSV","Se han importado correctamente %s Managers."%str(i))


    except sqlite3.OperationalError:

         messagebox.showerror("Error","Debe conectar la Base de datos primero")

    except Exception as e:

        messagebox.showerror("%s : Error : Los registros ya fueron cargados"%e)

# Valido si hay Owners cargados
def getOwner():

    connection = sqlite3.connect("administration_db")
    cursor = connection.cursor()
    bool = True

    try:

        cursor.execute("SELECT count(*) FROM MANAGERS")
        result_set = cursor.fetchall()
        connection.commit()
        connection.close()

        for i in result_set:

            if i[0] == 0:

                bool = False

    except sqlite3.OperationalError:

        pass


    return bool

#Valido que se haya cargado algun Manager del archivo .csv
def getManager():

    connection = sqlite3.connect("administration_db")
    cursor = connection.cursor()
    bool = True

    try:

        cursor.execute("SELECT count(*) FROM MANAGERS")
        result_set = cursor.fetchall()
        connection.commit()
        connection.close()

        for i in result_set:

            if i[0] == 0:

                bool = False

    except sqlite3.OperationalError:

        pass


    return bool

# Cargo datos del Owner e inserto las base de datos (.JSON)
def loadJson():

    errors = 0
    i = 1

    with open('data.json') as file:

        # Leo JSON
        data = json.load(file)

        # Recorro JSON
        for dbase in data['db_list']:

            #Contador para ver en consola
            print ("\nREGISTRO NUMERO %s "%i)

            # ------ COMIENZO LECTURA Y ASIGNACION DATOS DEL JSON -------------

            db_name = dbase.get('dn_name')

            name = dbase.get('owner', None)
            if name:
                name = name.get('name')
                name_ok,lastname_ok = separateName(name)


            username = dbase.get('owner')
            if username:
                username = username.get('uid', None)


            email = dbase.get('owner',None)
            if email:
                email = email.get('email')

            # Funcion que separa el nombre en : primer nombre y apellido : (Jose luis Perez) --> Jose Perez
            first_name,lastname = separateName(name)

            # Creo email con el criterio : primerNombre.apellido@mercadolibre.com : jose.luis.perez@mercado.. --> jose.perez@mercado..
            email = createEmail(first_name.lower(),lastname.lower())


            time_stamp = dbase.get('owner',None)
            if time_stamp:
                time_stamp = time_stamp.get('time_stamp')


            confidentiality = dbase.get('classification',None)
            if confidentiality:
                confidentiality = confidentiality.get('confidentiality')


            integrity = dbase.get('classification',None)
            if integrity:
                integrity = integrity.get('integrity')


            availability = dbase.get('classification',None)
            if availability:
                availability = availability.get('availability')

            #Valido y creo campos (ver en la funcion mas detalle)
            validateJson(db_name,name,email,username)

            # Si se cargaron los Managers (.csv) - sigo..
            if getManager() :

                try:

                    # Inserto nuevo Owner en la base de datos
                    inserted_owner_id = insertOwner(name_ok,lastname_ok,username,email,time_stamp)

                    # Creo una instancia de la clase Owner()
                    owner_db = Owner(inserted_owner_id,name_ok,lastname_ok,username,email,time_stamp)

                    # Agrego la instancia al objeto Owner de tipo : clase OwnerList()  --> lista que contendra todos los Owners
                    owner_db_list.addOwner(owner_db)

                    # Busco el manager por clave username . Devuelve boolean , id manager y email
                    have_manager,manager_id,manager_email = searchManager(username)

                    # Si la base de datos tiene un Manager asignado - sigo..
                    if have_manager:

                        # La base de datos debe tener obligatoriamente los valores para clasificarla
                        if confidentiality and integrity and availability:

                                try:

                                    # Calculo la clasificacion final de la nueva BD y la inserto en la base de datos
                                    final_classification = calculateClassification(confidentiality,integrity,availability)
                                    inserted_db_id = insertDatabase(manager_id,inserted_owner_id,confidentiality,integrity,availability,db_name,final_classification)

                                    # Creo una instancia de la clase Databases()

                                    new_database = Databases(inserted_db_id,manager_id,inserted_owner_id,db_name,confidentiality,integrity,availability,final_classification)

                                    # Agrego la instancia al objeto db_list de tipo : clase DBList()  --> lista que contendra todas las bases registradas
                                    db_list.addDB(new_database)

                                    #Obtengo nombre de manager
                                    name_manager = separateEmail(manager_email)

                                    #Inserto datos a visualizar en tabla de interfaz
                                    interface.tree.insert('',0,text = "           "+db_name, values = ("      "+name_manager,"    "+name,"          "+final_classification))


                                except Exception as e:

                                    messagebox.showwarning("Atencion!","No se pudo cargar la Base %s perteneciente a %s %s. Ya existe una base de datos con ese nombre."% (str(db_name.upper()),str(name_ok),str(lastname_ok)))
                                    errors +=1
                                    i += 1


                        else:

                            messagebox.showwarning("Atencion!","No se pudo registrar la base de datos %s ya que alguno de sus indicadores para clasificacion: integrity,confidentiality o availability es nulo. Revise los datos y vuelva a ingresarla"%db_name.upper())
                            errors +=1
                            i += 1
                    else:

                        messagebox.showwarning("Atencion!","No se pudo cargar la Base  %s . Por favor valide que tenga un Manager asociado.Se envio un email a %s %s para validar la informacion"% (str(db_name.upper()),str(name_ok.upper()),str(lastname_ok.upper())))
                        errors +=1
                        i += 1

                except sqlite3.OperationalError as e:

                    messagebox.showerror("Error!","Debe conectar la base de datos primero")
                    break

                except sqlite3 as e:

                    messagebox.showerror("Error!","El owner %s ya fue registrado con la BD %s"% (str(name.upper()),str(db_name.upper())))

                    errors +=1
                    i += 1

            else:

                messagebox.showerror("Error!","Primero debe ingresar los Managers(.CSV)")
                break

            i += 1




# ********************** /// ***************************************************



    if i > 2:
        messagebox.showinfo("IMPORT FINALIZADO","Resgistros procesados %s\nBases ingresadas : %s\nBases con errores : %s"% (str(len(data['db_list'])),(len(data['db_list'])-errors),str(errors)))




if __name__ == '__main__':

    window = Tk()
    interface = GUI(window)
    window.mainloop()

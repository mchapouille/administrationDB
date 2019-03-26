class Databases():

    def __init__(self,database_id,manager_id,owner_id,name,confidentiality,integrity,availability,final_classification):

        self.database_id = database_id
        self.manager_id = manager_id
        self.owner_id = owner_id
        self.name = name
        self.confidentiality = confidentiality
        self.integrity = integrity
        self.availability = availability
        self.final_classification = final_classification


class DBlist():

    databases = []

    def addDB(self,database):

        self.databases.append(database)


    def showDBList(self):

        for i in self.databases:
            print(i)

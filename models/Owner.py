class Owner():

    def __init__(self,owner_id,name,lastname,username,email,time_stamp):

        self.owner_id = owner_id
        self.name = name
        self.lastname = lastname
        self.username = username
        self.email = email
        self.time_stamp = time_stamp

class OwnerList():

    owners = []

    def addOwner(self,owner):

        self.owners.append(owner)

    def showOwners(self):

        for o in self.owners:
            print(o)

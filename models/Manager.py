class Manager():

    def __init__(self,manager_id,username,state,email):

        self.manager_id = manager_id
        self.username = username
        self.state = state
        self.email = email


class ManagerList():

    managers = []

    def addManager(self,manager):

        self.managers.append(manager)


    def showManagers(self):

        for o in self.managers:
            print(o)

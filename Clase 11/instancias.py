class PartyAnimal:
   x = 0
   name = ""
   def __init__(self, z):
     self.name = z
     print(self.name,"construido")

   def party(self) :
     self.x = self.x + 1
     print(self.name,"recuento",self.x)

s = PartyAnimal("ESTEBAN")
j = PartyAnimal("JUAN")

s.party()
j.party()
s.party()
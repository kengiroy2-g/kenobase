
from datetime import date
class User:
    """ avec cette classe on pourrra experimenter sur la creation des objets"""
    def __init__(self, full_name, birthday):
        self.full_name = full_name
        self.birthday = birthday # yyyymmdd
        # extract first and last name
        name_piece = full_name.split(" ")
        self.first_name =name_piece[0]
        self.last_name =name_piece[1]
    def age(self):
        """ return the age of the user"""
        #return the date of today
        today = date.today()
    
        # extract the date from parameter biertday
        yyyy = int(self.birthday[0:4])
        mm = int(self.birthday[4:6])
        dd = int(self.birthday[6:8])
        b_day = date(  yyyy, mm, dd)
        # Computer age in days
        age_in_day = (today -b_day ).days
        age_in_year = age_in_day / 365
        return int(age_in_year)


user1 = User("nangue ghislain", "19850503")
print(user1.__init__)
print(user1.last_name)

print("age de " + str(user1.age())+ " ans")
# help(date)
print(dir())
 
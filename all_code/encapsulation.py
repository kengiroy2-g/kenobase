class PhoneBook:
    def __init__(self):
        self.__entries = {}
    def add(self, name, phone):
        assert str(name).title() not in self.__entries, "Name ist bereit vergeben"
        self.__entries[str(name).title()] = phone
    def get_phone(self, name):
        print(self.__entries[name])
        # print(self.__entries[name1])
        return self.__entries[name]

buch = PhoneBook()
buch.add("Jason", "0176000")
buch.add("Armel", "0187000")
# buch.__entries["Jason"] = "00224400"
buch.get_phone("Jason")

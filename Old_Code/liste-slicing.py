students = ["Max", "Monika", "Erik", "Tim", "Brain"]
test_string = "paypal einkauf bei xyz"
a = 0
b = 0
# print(students[1:-1])
liste = test_string.split()
for element in liste:
    students.append(element)
print(students)
print(test_string[-3:2])
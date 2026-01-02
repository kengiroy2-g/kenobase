# Defining the original number series XX
XX = [1, 4, 7, 16, 18, 19, 24, 26, 28, 37, 38, 47, 49, 50, 51, 56, 58, 65, 67, 68, 70]

# Adding 5 to each number in XX, then adding 7 to each result
XX_1 = [x + 4 for x in XX]
#XX_2 = [x + 7 for x in XX]

# Subtracting 5 from each number in XX, then subtracting 7 from each result
XX_11 = [x - 4 for x in XX]
#XX_22 = [x - 7 for x in XX]
# Combining XX_1 and XX_2 into one series, removing negative numbers and numbers greater than 70
# and ensuring each number appears only once
XX_3 = list(set([x for x in XX_1 + XX_11  if 0 < x <= 70]))

XX_3.sort()  # Sorting the final series for better readability
print(XX_3)

# Defining the given series
series = XX_3

# Generating a list of numbers from 1 to 70
numbers_1_to_70 = set(range(1, 71))

# Finding numbers between 1 and 70 that are not in the given series
numbers_not_in_series = list(numbers_1_to_70 - set(series))

# Sorting the list for better readability
numbers_not_in_series.sort()
print(numbers_not_in_series)

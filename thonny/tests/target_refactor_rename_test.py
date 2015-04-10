#partly inspired by http://www.programiz.com/python-programming/examples/calculator

from source_refactor_rename_test import Calculator    #<<<<<<<LINE T1>>>>>>>

print("Select operation:")
print("1: Add")
print("2: Subtract")

choice = input("Enter choice(1/2):")

num1 = int(input("Enter first number: "))
num2 = int(input("Enter second number: "))

calculator = Calculator()       #<<<<<<<LINE T2>>>>>>>

if choice == '1':
   print(num1,"+",num2,"=", calculator.sumtogether(num1,num2))    #<<<<<<<LINE T3>>>>>>>

elif choice == '2':
   print(num1,"-",num2,"=", calculator.subtract(num1,num2))       #<<<<<<<LINE T4>>>>>>>

else:
   print("Invalid input")
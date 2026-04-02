def fib(n):
  pred,curr = 0,1
  k = 1
  while k < n:
    pred, curr = curr,pred + curr
    k = k + 1
  return curr

assert 3 > 2, "True"

# def make_adder(n):
#   def adder(k):
#     return k + n
#   return adder
# print(make_adder(1)(2))
for i in range(9):
  print(i)
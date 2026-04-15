def tree(root_label,branches = []):
    for branch in branches:
        assert is_tree(branches),'分支必须是树'
    return [root_label] + list(branches)

def label(tree):
    return tree[0]
def branches(tree):
    return tree[1:]

def is_tree(tree):
    if type(tree) != list or len(tree) == 0:
        return False
    for branch in branches(tree):
        if not is_tree(branch):
            return False
    return True

def is_leaf(tree):
    return not branches(tree)

def fib_tree(n):
    if n == 0 or n == 1:
        return tree(n)
    else:
        left, right = fib_tree(n-2),fib_tree(n-1)
        fib_n = label(left) + label(right)
        return tree(fib_n,[left, right])

# print(fib_tree(5))

def count_leaves(tree):
    if is_leaf(tree):
        return 1
    else:
        branch_counts = [count_leaves(b) for b in branches(tree)] 
        return sum(branch_counts)

from unicodedata import name,lookup

print(name('A'))
print(lookup('WHITE SMILING FACE'))
print(lookup('BABY'))
print(lookup('SOCCER BALL').encode())



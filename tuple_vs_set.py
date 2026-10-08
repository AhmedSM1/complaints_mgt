"""
Tuple vs Set in Python

tuple: ordered, allows duplicates, immutable (cannot change after creation)
set:   unordered, unique values only, mutable (can add/remove items)
"""


def show_tuple():
    # Created with parentheses. Order is kept. Duplicates are allowed.
    colors = ("red", "green", "blue", "red")
    print("TUPLE")
    print("  value:     ", colors)
    print("  type:      ", type(colors))
    print("  ordered:   ", colors[0], colors[1])  # indexing works
    print("  duplicates:", colors.count("red"), "times 'red'")
    print("  immutable: you cannot do colors[0] = 'yellow'")
    print("  hashing:   can be used as a dict key")
    lookup = {("lat", 30.0): "Cairo"}
    print("  dict key:  ", lookup[("lat", 30.0)])
    print()


def show_set():
    # Created with curly braces. Order is not guaranteed. Duplicates vanish.
    colors = {"red", "green", "blue", "red"}
    print("SET")
    print("  value:     ", colors)  # 'red' appears only once
    print("  type:      ", type(colors))
    print("  unique:    duplicates were removed automatically")
    print("  no index:  colors[0] would raise TypeError")
    print("  mutable:   you can add and remove items")
    colors.add("yellow")
    colors.discard("green")
    print("  after edit:", colors)
    print("  hashing:   a set itself cannot be a dict key (unhashable)")
    print()


def show_operations():
    a = {1, 2, 3, 4}
    b = {3, 4, 5, 6}
    print("SET MATH (not available on tuples)")
    print("  a:         ", a)
    print("  b:         ", b)
    print("  union:     ", a | b)       # {1, 2, 3, 4, 5, 6}
    print("  intersection:", a & b)     # {3, 4}
    print("  difference:", a - b)       # {1, 2}
    print()

    coords = (10, 20)
    print("TUPLE UNPACKING (natural for fixed-size records)")
    x, y = coords
    print("  coords:    ", coords)
    print("  x, y:      ", x, y)


if __name__ == "__main__":
    show_tuple()
    show_set()
    show_operations()

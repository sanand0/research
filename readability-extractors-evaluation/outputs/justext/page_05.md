The list data type has some more methods. Here are all of the methods of list
objects:

list.append(x)

Add an item to the end of the list. Similar to a[len(a):]=[x].

list.extend(iterable)

Extend the list by appending all the items from the iterable. Similar to
a[len(a):]=iterable.

list.insert(i, x)

Insert an item at a given position. The first argument is the index of the
element before which to insert, so a.insert(0,x) inserts at the front of
the list, and a.insert(len(a),x) is equivalent to a.append(x).

list.remove(x)

Remove the first item from the list whose value is equal to x. It raises a
ValueError if there is no such item.

list.pop([i])

Remove the item at the given position in the list, and return it. If no index
is specified, a.pop() removes and returns the last item in the list.
It raises an IndexError if the list is empty or the index is
outside the list range.

list.clear()

Remove all items from the list. Similar to dela[:].

list.index(x[, start[, end]])

Return zero-based index of the first occurrence of x in the list.
Raises a ValueError if there is no such item.

The optional arguments start and end are interpreted as in the slice
notation and are used to limit the search to a particular subsequence of
the list. The returned index is computed relative to the beginning of the full
sequence rather than the start argument.

list.count(x)

Return the number of times x appears in the list.

list.sort(*, key=None, reverse=False)

Sort the items of the list in place (the arguments can be used for sort
customization, see sorted() for their explanation).

You might have noticed that methods like insert, remove or sort that
only modify the list have no return value printed – they return the default
None. [1] This is a design principle for all mutable data structures in
Python.

Another thing you might notice is that not all data can be sorted or
compared. For instance, [None,'hello',10] doesn’t sort because
integers can’t be compared to strings and None can’t be compared to
other types. Also, there are some types that don’t have a defined
ordering relation. For example, 3+4j<5+7j isn’t a valid
comparison.

The list methods make it very easy to use a list as a stack, where the last
element added is the first element retrieved (“last-in, first-out”). To add an
item to the top of the stack, use append(). To retrieve an item from the
top of the stack, use pop() without an explicit index. For example:

It is also possible to use a list as a queue, where the first element added is
the first element retrieved (“first-in, first-out”); however, lists are not
efficient for this purpose. While appends and pops from the end of list are
fast, doing inserts or pops from the beginning of a list is slow (because all
of the other elements have to be shifted by one).

To implement a queue, use collections.deque which was designed to
have fast appends and pops from both ends. For example:

>>> fromcollectionsimportdeque>>> queue=deque(["Eric","John","Michael"])>>> queue.append("Terry")# Terry arrives>>> queue.append("Graham")# Graham arrives>>> queue.popleft()# The first to arrive now leaves'Eric'>>> queue.popleft()# The second to arrive now leaves'John'>>> queue# Remaining queue in order of arrivaldeque(['Michael', 'Terry', 'Graham'])

List comprehensions provide a concise way to create lists.
Common applications are to make new lists where each element is the result of
some operations applied to each member of another sequence or iterable, or to
create a subsequence of those elements that satisfy a certain condition.

Note that this creates (or overwrites) a variable named x that still exists
after the loop completes. We can calculate the list of squares without any
side effects using:

squares=list(map(lambdax:x**2,range(10)))

or, equivalently:

squares=[x**2forxinrange(10)]

which is more concise and readable.

A list comprehension consists of brackets containing an expression followed
by a for clause, then zero or more for or if
clauses. The result will be a new list resulting from evaluating the expression
in the context of the for and if clauses which follow it.
For example, this listcomp combines the elements of two lists if they are not
equal:

There is a way to remove an item from a list given its index instead of its
value: the del statement. This differs from the pop() method
which returns a value. The del statement can also be used to remove
slices from a list or clear the entire list (which we did earlier by assignment
of an empty list to the slice). For example:

We saw that lists and strings have many common properties, such as indexing and
slicing operations. They are two examples of sequence data types (see
Sequence Types — list, tuple, range). Since Python is an evolving language, other sequence data
types may be added. There is also another standard sequence data type: the
tuple.

A tuple consists of a number of values separated by commas, for instance:

As you see, on output tuples are always enclosed in parentheses, so that nested
tuples are interpreted correctly; they may be input with or without surrounding
parentheses, although often parentheses are necessary anyway (if the tuple is
part of a larger expression). It is not possible to assign to the individual
items of a tuple, however it is possible to create tuples which contain mutable
objects, such as lists.

Though tuples may seem similar to lists, they are often used in different
situations and for different purposes.
Tuples are immutable, and usually contain a heterogeneous sequence of
elements that are accessed via unpacking (see later in this section) or indexing
(or even by attribute in the case of namedtuples).
Lists are mutable, and their elements are usually homogeneous and are
accessed by iterating over the list.

A special problem is the construction of tuples containing 0 or 1 items: the
syntax has some extra quirks to accommodate these. Empty tuples are constructed
by an empty pair of parentheses; a tuple with one item is constructed by
following a value with a comma (it is not sufficient to enclose a single value
in parentheses). Ugly, but effective. For example:

The statement t=12345,54321,'hello!' is an example of tuple packing:
the values 12345, 54321 and 'hello!' are packed together in a tuple.
The reverse operation is also possible:

>>> x,y,z=t

This is called, appropriately enough, sequence unpacking and works for any
sequence on the right-hand side. Sequence unpacking requires that there are as
many variables on the left side of the equals sign as there are elements in the
sequence. Note that multiple assignment is really just a combination of tuple
packing and sequence unpacking.

Python also includes a data type for sets. A set is an unordered collection
with no duplicate elements. Basic uses include membership testing and
eliminating duplicate entries. Set objects also support mathematical operations
like union, intersection, difference, and symmetric difference.

Curly braces or the set() function can be used to create sets. Note: to
create an empty set you have to use set(), not {}; the latter creates an
empty dictionary, a data structure that we discuss in the next section.

Here is a brief demonstration:

>>> basket={'apple','orange','apple','pear','orange','banana'}>>> print(basket)# show that duplicates have been removed{'orange', 'banana', 'pear', 'apple'}>>> 'orange'inbasket# fast membership testingTrue>>> 'crabgrass'inbasketFalse>>> # Demonstrate set operations on unique letters from two words>>>>>> a=set('abracadabra')>>> b=set('alacazam')>>> a# unique letters in a{'a', 'r', 'b', 'c', 'd'}>>> a-b# letters in a but not in b{'r', 'd', 'b'}>>> a|b# letters in a or b or both{'a', 'c', 'r', 'd', 'b', 'm', 'z', 'l'}>>> a&b# letters in both a and b{'a', 'c'}>>> a^b# letters in a or b but not both{'r', 'd', 'b', 'm', 'z', 'l'}

Another useful data type built into Python is the dictionary (see
Mapping Types — dict). Dictionaries are sometimes found in other languages as
“associative memories” or “associative arrays”. Unlike sequences, which are
indexed by a range of numbers, dictionaries are indexed by keys, which can be
any immutable type; strings and numbers can always be keys. Tuples can be used
as keys if they contain only strings, numbers, or tuples; if a tuple contains
any mutable object either directly or indirectly, it cannot be used as a key.
You can’t use lists as keys, since lists can be modified in place using index
assignments, slice assignments, or methods like append() and
extend().

It is best to think of a dictionary as a set of key: value pairs,
with the requirement that the keys are unique (within one dictionary). A pair of
braces creates an empty dictionary: {}. Placing a comma-separated list of
key:value pairs within the braces adds initial key:value pairs to the
dictionary; this is also the way dictionaries are written on output.

The main operations on a dictionary are storing a value with some key and
extracting the value given the key. It is also possible to delete a key:value
pair with del. If you store using a key that is already in use, the old
value associated with that key is forgotten.

Extracting a value for a non-existent key by subscripting (d[key]) raises a
KeyError. To avoid getting this error when trying to access a possibly
non-existent key, use the get() method instead, which returns
None (or a specified default value) if the key is not in the dictionary.

Performing list(d) on a dictionary returns a list of all the keys
used in the dictionary, in insertion order (if you want it sorted, just use
sorted(d) instead). To check whether a single key is in the
dictionary, use the in keyword.

To loop over two or more sequences at the same time, the entries can be paired
with the zip() function.

>>> questions=['name','quest','favorite color']>>> answers=['lancelot','the holy grail','blue']>>> forq,ainzip(questions,answers):... print('What is your {0}? It is {1}.'.format(q,a))...What is your name? It is lancelot.What is your quest? It is the holy grail.What is your favorite color? It is blue.

To loop over a sequence in reverse, first specify the sequence in a forward
direction and then call the reversed() function.

>>> foriinreversed(range(1,10,2)):... print(i)...97531

To loop over a sequence in sorted order, use the sorted() function which
returns a new sorted list while leaving the source unaltered.

The conditions used in while and if statements can contain any
operators, not just comparisons.

The comparison operators in and notin are membership tests that
determine whether a value is in (or not in) a container. The operators is
and isnot compare whether two objects are really the same object. All
comparison operators have the same priority, which is lower than that of all
numerical operators.

Comparisons can be chained. For example, a<b==c tests whether a is
less than b and moreover b equals c.

Comparisons may be combined using the Boolean operators and and or, and
the outcome of a comparison (or of any other Boolean expression) may be negated
with not. These have lower priorities than comparison operators; between
them, not has the highest priority and or the lowest, so that AandnotBorC is equivalent to (Aand(notB))orC. As always, parentheses
can be used to express the desired composition.

The Boolean operators and and or are so-called short-circuit
operators: their arguments are evaluated from left to right, and evaluation
stops as soon as the outcome is determined. For example, if A and C are
true but B is false, AandBandC does not evaluate the expression
C. When used as a general value and not as a Boolean, the return value of a
short-circuit operator is the last evaluated argument.

It is possible to assign the result of a comparison or other Boolean expression
to a variable. For example,

Note that in Python, unlike C, assignment inside expressions must be done
explicitly with the
walrus operator:=.
This avoids a common class of problems encountered in C programs: typing =
in an expression when == was intended.

Sequence objects typically may be compared to other objects with the same sequence
type. The comparison uses lexicographical ordering: first the first two
items are compared, and if they differ this determines the outcome of the
comparison; if they are equal, the next two items are compared, and so on, until
either sequence is exhausted. If two items to be compared are themselves
sequences of the same type, the lexicographical comparison is carried out
recursively. If all items of two sequences compare equal, the sequences are
considered equal. If one sequence is an initial sub-sequence of the other, the
shorter sequence is the smaller (lesser) one. Lexicographical ordering for
strings uses the Unicode code point number to order individual characters.
Some examples of comparisons between sequences of the same type:

Note that comparing objects of different types with < or > is legal
provided that the objects have appropriate comparison methods. For example,
mixed numeric types are compared according to their numeric value, so 0 equals
0.0, etc. Otherwise, rather than providing an arbitrary ordering, the
interpreter will raise a TypeError exception.
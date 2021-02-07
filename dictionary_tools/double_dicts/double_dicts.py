import bijective_double_dict

#fixme comment on enums
# fixme larger rework. Multiplicity clarification. Currently multiplicity (
#  updating with key,
# value pair that already exists is not tracked). Test for this

class DoubleDict(bijective_double_dict.BijectiveDoubleDict):
    """
    Standardizing creating a dictionary and at same time the inverse
    dictionary. Additionally using ordered dicts for additional info/indexing
    Python 3.7 has dicts as ordered by standard now.
    """

    def __init__(self, MULTIPLICITY=False):
        super().__init__()
        self.MULTIPLICITY = MULTIPLICITY

        # as we begin with empty dicts we have injectivity in a sense
        self.forward_injective = True

        # We have not seen any 1 key map to
        # several values yet when we start, the forward dict is not multi-valued
        self.forward_multivalued = False
    def helper(self, d0, key, value, ALLOW_APPEND=True):
        """ fixme Explanation.

        :param d0:
        :param key:
        :param value:
        :param ALLOW_APPEND:
        :return:
        """

        # updates and handles the cases of value being a list or not and whether current entry is list or not
        VALUE_IS_LIST = (type(value) == list)  # check if the value is a list.
        if VALUE_IS_LIST:  # is the value provided is a list, assume
            # multivalued forward function. I.e. as a map from a key to each
            # of the values in the list. Not as a map from key to the list as
            # one object! By convention
            self.forward_multivalued = True

        d0.setdefault(key, default=[])
        if key in d0:
            if value not in d0[key] or self.MULTIPLICITY:
                d0[key].append(value)

    def update(self, tuple_list0, ALLOW_APPEND=False):
        for key, value in tuple_list0:  # dict_of_updates.items():
            assert type(key) in [list, int, str]
            for v in value:
                self.helper(self.dict_forward, key, v)
                self.helper(self.dict_inverse, v, key)


def test_function0():
    alphabet = "abcd"
    for MULTIPLICITY in [True, False]:
        dd1 = DoubleDict(MULTIPLICITY)
        tl1 = [(i, v) for i, v in enumerate(alphabet)]
        tl1_rev = [(v, i) for i, v in enumerate(alphabet)]
        tl1_forward_answer = [(x[0], [x[1]]) for x in tl1]
        tl1_rev_answer = [(x[0], [x[1]]) for x in tl1_rev]
        if MULTIPLICITY:
            tl1_forward_answer[1] = (tl1_forward_answer[1][0], ["b", "b"])
            tl1_forward_answer[2] = (tl1_forward_answer[2][0], ["c", "c"])
            print("tl1_forward_answer: ", tl1_forward_answer)

            tl1_rev_answer[1] = (tl1_rev_answer[1][0], [1, 1])
            tl1_rev_answer[2] = (tl1_rev_answer[2][0], [2, 2])
            print("tl1_rev_answer: ", tl1_rev_answer)

        dd1.update(tl1)
        dd1.update(tl1[1:3])
        print(list(dd1.dict_forward.items()))
        print(list(dd1.dict_inverse.items()))

        assert list(dd1.dict_forward.items()) == [(v[0], v[1]) for v in
                                                  tl1_forward_answer]
        assert list(dd1.dict_inverse.items()) == [(v[0], v[1]) for v in
                                                  tl1_rev_answer]
    print("test 0 passed")


def test_function1():
    dd1 = DoubleDict()
    alphabet = "abcd"
    tl1 = [(i, v) for i, v in enumerate(alphabet)]
    tl1_rev = [(v, i) for i, v in enumerate(alphabet)]
    dd1.update(tl1)
    assert list(dd1.dict_forward.items()) == [(v[0], [v[1]]) for v in tl1]
    assert list(dd1.dict_inverse.items()) == [(v[0], [v[1]]) for v in tl1_rev]
    print("test 1 passed")


def test_function2():
    dd1 = DoubleDict()
    alphabet = "abcd"
    tl1 = [(i, v) for i, v in enumerate(alphabet)]
    tl1.append((11, 'b'))  # now b needs to map to both 1 and 11
    dd1.update(tl1, ALLOW_APPEND=True)
    assert list(dd1.dict_forward.items()) == [(v[0], [v[1]]) for v in tl1]
    assert list(dd1.dict_inverse.items()) == [('a', [0]), ('b', [1, 11]),
                                              ('c', [2]), ('d', [3])]
    print("test 2 passed")


def test_function3():
    dd1 = DoubleDict()
    alphabet = "abcd"
    tl1 = [(i, v) for i, v in enumerate(alphabet)]
    # adding more values to key "1" to test one-to-many
    tl1.append((1, 'x'))
    tl1.append((1, 'y'))
    tl1.append((1, 'z'))
    dd1.update(tl1, ALLOW_APPEND=True)
    assert list(dd1.dict_forward.items()) == [(0, ['a']),
                                              (1, ['b', 'x', 'y', 'z']),
                                              (2, ['c']), (3, ['d'])]
    print("test 3 passed")

    assert sorted(list(dd1.dict_inverse.items()), key=lambda x: x[0]) == sorted(
        [('a', [0]), ('b', [1]), ('c', [2]), ('d', [3]), ('z', [1]), ('x', [1]),
         ('y', [1])], key=lambda x: x[0])
    # forming a double dict from the previous should make the inverse align with first forward
    dd2 = DoubleDict()
    dd2.update(list(dd1.dict_inverse.items()), ALLOW_APPEND=True)
    assert dd2.dict_inverse == dd1.dict_forward
    assert dd1.dict_inverse == dd2.dict_forward


if __name__ == "__main__":
    test_function0()
    test_function1()
    test_function2()
    test_function3()

"""Small module to implement a dictionary which simultaneously maps inverse dictionary.
Has common dunder methods implemented for printing, getting, setting.  Iterations coming next.
A second module will extend with multivalued handling.
"""

import collections  # For ordered dict. Note Python 3 now has ordered dict.
import itertools  # only for example, not used in implementation


class DictJsonHandler:
    def __init__(self):
        pass

    def make_ordered_dict_jsonable(self, ordered_dict):
        """
        Unsure if json'ing a dict reliably preserves order. (At least not in all python versions and dict types)
        fixme Add assertions of jsonable types within.

        :param ordered_dict:
        :return: dictionary with keys and values as lists to ensure order
        preservation
        """
        key_list = []
        value_list = []
        for j, (key, value) in enumerate(ordered_dict.items()):
            key_list.append(key)
            value_list.append(value)
        return {"type": "ordered_dict",
                "data": {"keys": key_list, "values": value_list}}


    def recreate_ordered_dict_from_json(self, jsoned_ordered_dict):
        """
        Recreate an ordered dict from one stored in the json format from the
        function above.

        :param jsoned_ordered_dict:
        :return: Ordered dictionary from the json'ed format
        """
        out = collections.OrderedDict()
        assert len(jsoned_ordered_dict["data"]["keys"]) == len(
            jsoned_ordered_dict["data"]["values"])
        for j, key in enumerate(jsoned_ordered_dict["data"]["keys"]):
            out[key] = jsoned_ordered_dict["data"]["values"][j]
        return out


class BijectiveDoubleDict:
    """
    A class maintaining a regular dictionary of key, value but also forms
    an inverse value, key dictionary. Helps warn about overwriting, or loss
    of surjectivity/injectivity.
    """

    def __init__(self):
        self.dict_forward = collections.OrderedDict()
        self.dict_inverse = collections.OrderedDict()
        self.dict_jason_handler = DictJsonHandler()

    def update(self, tuple_list0, CHECK_AT_END=False):
        """

        :param tuple_list0: list of tuples where each tuple t = (key,value)
        will be key, values in the dictionary
        :param CHECK_AT_END: Flag to run a consistency check.
        :return: None, updates instance variables
        """
        for key, value in tuple_list0:
            # fixme should probably make better exception handling. Allowed types as well could be updated
            assert type(key) in [tuple, int, str]
            assert type(value) in [tuple, int, str]
            assert key not in self.dict_forward
            assert value not in self.dict_inverse

            self.dict_forward.update({key: value})
            self.dict_inverse.update({value: key})
        if CHECK_AT_END:
            self.check_consistency()

    def json_it(self):
        """
        Forms a dictionary containing all the info the bij. double dict,
        assuming the key/values put into it themselves were jsonable in the
        first place
        :return: dict
        """
        out = {"type": "dd", "data": {
            "forward": self.dict_jason_handler.make_ordered_dict_jsonable(
                self.dict_forward),
            "inverse": self.dict_jason_handler.make_ordered_dict_jsonable(
                self.dict_inverse)}}
        return out

    def create_from_json(self, x):
        """
        Takes .json file contents created by json_it.

        :param x: .json file contents
        :return: None, overwrites within self
        """
        self.dict_forward = self.dict_jason_handlerrecreate_ordered_dict_from_json(
            x["data"]["forward"])
        self.dict_inverse = self.dict_jason_handlerrecreate_ordered_dict_from_json(
            x["data"]["inverse"])

    def get_forward(self, key):
        """Look up a key in the forward direction."""
        return self.dict_forward[key]

    def get_inverse(self, key):
        """Look up a key(forward value) in the backward/inverse direction."""
        return self.dict_inverse[key]

    def get_forward_by_order(self, n):
        """Retrieve from forward by ordered position."""
        return itertools.islice(self.dict_forward.items(), n, n + 1)

    def get_inverse_by_order(self, n):
        """Retrieve from inverse by ordered position."""
        return itertools.islice(self.dict_inverse.items(), n, n + 1)

    def check_consistency(self):
        """Checking for consistency between forward and inverse."""
        CHECK = True
        for key, values in self.dict_forward.items():
            # This should work even in later multivalued extensions
            if not type(values) is list:
                values = [values]
            for v in values:
                if v not in self.dict_inverse:
                    CHECK = False
                    break
                else:
                    assert self.dict_inverse[v] == key
        assert CHECK  # fixme should probably make better exception handling
        print("Consistency test passed")

    def __str__(self):
        return str(self.dict_forward) + ";\n" + str(self.dict_inverse)

    def __repr__(self):
        return self.__str__()

    def __setitem__(self, key, value):
        self.update([(key, value)], CHECK_AT_END=False)

    def __getitem__(self, item):
        """Default behavior will be to work with forward dict for now."""
        return self.dict_forward[item]

    def __len__(self):
        """Returns the length of the forward dictionary - not the inverse."""
        return len(self.dict_forward)

    # def __iter__(self):
    #     return self
    #
    # def __next__(self):
    #     return self.dict_forward.__next__()


def example1():
    print("Example 1: Multi-index to a linear index (and vice versa)")
    dims0 = (3, 5, 4)
    tuple_list_gen = enumerate(itertools.product(*[range(0, m) for m in dims0]))
    bdd_1 = BijectiveDoubleDict()
    bdd_1.update(tuple_list_gen, CHECK_AT_END=True)
    print(bdd_1)


def example2():
    """Needs asserts or something to actually fail."""
    chars = "ABCDEF"
    bdd_2 = BijectiveDoubleDict()
    bdd_2.update(((c, i + 65) for i, c in enumerate(chars)), CHECK_AT_END=True)
    test_key = "B"
    test_key_1 = "A"

    test_key_2 = "additional_dunder test"
    test_value_2 = "XYZ"
    bdd_2[test_key_2] = test_value_2

    print(
        "\nExample 2: Small ASCII inspired example. (Many ways of pulling this info naturally exists). Simply an example of a useful renaming.")

    print("get forward %s " % test_key, bdd_2.get_forward(test_key))
    print("testing dunder methods: get_item %s: " % test_key_1,
          bdd_2[test_key_1])
    print("...")

    print(bdd_2)  # testing print str, repr dunders too
    print("testing dunder methods: set_item %s, %s : " % (
        test_key_2, test_value_2))

    print(bdd_2)


def test_json():
    d = collections.OrderedDict()

    """Check if non-empty dict breaks the reconstruction below. Expecting it to
    be overwritten."""

    d["7"] = "value7"
    # generate som test data
    for i, c in enumerate("abcdefghijkl"):
        d[i + 100] = c

    dict_jason_handler1 = DictJsonHandler()
    jsoned_ordered_dict = dict_jason_handler1.make_ordered_dict_jsonable(d)
    d_rec = dict_jason_handler1.recreate_ordered_dict_from_json(
        jsoned_ordered_dict)
    print(d_rec)
    assert (d == d_rec)
    print("json reconstruction test passed")


if __name__ == "__main__":
    example1()
    example2()
    test_json()

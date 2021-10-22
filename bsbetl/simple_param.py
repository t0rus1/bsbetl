''' a simple parameter container class for use by our all_table calcs and ov_calcs'''


class SimpleParam(dict):
    ''' simple structure to hold alltable and ov calculation parameters 

        we inherit from dict to allow easy json serialization and deserialization
    '''

    def __init__(self, name, calculation, min, max, setting, doc_ref):
        dict.__init__(self, name=name, calculation=calculation,
                      min=min, max=max, setting=setting, doc_ref=doc_ref)
        assert setting >= min and setting <= max, f"parameter '{name}' setting (={setting}) out of bounds ({min} -> {max})!"

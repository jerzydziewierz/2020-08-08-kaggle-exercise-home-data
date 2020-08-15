from warnings import warn

_numpy_available = False
try:
    import numpy as np
    _numpy_available = True
except:
    pass

_tensorflow_available = False
try:
    import tensorflow as tf
    _tensorflow_available = True
except:
    pass

class HandyDict(dict):
    """Provides matlab-like setting/storage of items in a dict (dictionary)

    q=handybeam.dict()
    q.new_key = 'Hello world!'
    print(q.new_key)


    happily copypasted from https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary , and modified only slightly.

    then, extended a bit.

    then, a bit more, with optional reprstyler. See self.__repr__();
    example reprstyler:

    q=handybeam.dict(zap=None,bald=6.28)

    def baldstyler(subject):
        return f'baldness score: {subject.bald:0.3f}'

    q.reprstyler=baldstyler

    q

    then, if you want a different styler for jupyter, and a different one for text-only, you can (optionally) override the reprstyler with reprstyler_html. It will only be used if _repr_html_ is called.

    def baldstyler2(subject):
        return f'<h1>baldness score: {subject.bald:0.3f}</h1>'
    q.reprstyler_html = baldstyler2


    You can still see the regular dict __repr__ (lists all keys/values) using
    super(handybeam.dict,q).__repr__()


    """
    def __init__(self, args={}, **kwargs):
        """ starts the instance.

        :param args: initial value in the dictionary.
        """
        super(HandyDict, self).__init__(args)
        if args is not None:
            if isinstance(args, dict):
                for k, v in args.items():
                    if not isinstance(v, dict):
                        self[k] = v
                    else:
                        self.__setattr__(k, HandyDict(v))

        # add a hard-coded value "reprstyler". This will be used to redirect repr to the given function

        # self.update({'reprstyler': None})  # Note: do not depend on this key being in the dictionary -- I might decide to not put it in as default
        for key, value in kwargs.items():
            self.update({key: value})

    def __getattr__(self, attr):
        """ responds to :code:`answer=dict.attribute`"""
        answer = self.get(attr)
        if answer is None:
            # skip warning if jupyter tries to access some typical methods
            if attr not in ('_ipython_canary_method_should_not_exist_',
                            '_ipython_display_',
                            '_repr_mimebundle_',
                            'reprstyler_html',
                            'reprstyler',
                            '_repr_markdown_',
                            '_repr_svg_',
                            '_repr_png_',
                            '_repr_pdf_',
                            '_repr_jpeg_',
                            '_repr_latex_',
                            '_repr_json_',
                            '_repr_javascript_',
                            'is_tensor_like',  # tensorflow uses this to check for tensors
                            ):
                # give meaningful error message:
                warn(f'no key "{attr}" in this dictionary. \nvalid keys are {[key for key in self.keys()]}', stacklevel=2)
                warn('in ', stacklevel=3)
                warn('in ', stacklevel=4)
                # attempt to continue by returning None:
        return self.get(attr)

    def __setattr__(self, key, value):
        """ responds to :code:`dict.key=value` """
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        """ responds to :code:`dict['key']=value` """
        super(HandyDict, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        """ ? I don't know what this does."""
        self.__delitem__(item)

    def __delitem__(self, key):
        """ ? I don't know what this does."""
        super(HandyDict, self).__delitem__(key)
        del self.__dict__[key]

    def __repr__(self):
        """
        If available, calls the reprstyler. If not available,just calls the default __repr__()
        """
        if self.reprstyler is not None:
            try:
                return self.reprstyler(self)
            except Exception as E:
                print(E)
                print('-- falling back to super...')
                return super(HandyDict, self).__repr__()
        else:  # if reprstyler not set
            return super(HandyDict, self).__repr__()

    def __str__(self):
        """just wrap to self.__repr__()"""
        return self.__repr__()

    def _repr_html_(self):
        if self.reprstyler_html is not None:
            try:
                return self.reprstyler_html(self)
            except Exception as reprstyler_html_fail:
                print(reprstyler_html_fail)
                print('-- falling back to super.__repr__() --')
                return super(HandyDict, self).__repr__()  # note that dict has no _repr_html_() to call.
        else:  # if reprstyler_html not set
            # at this point, if reprstyler is set, use it. Otherwise it will fall back too early and all Jupyter output would be bad.
            if self.reprstyler is not None:
                try:
                    return self.reprstyler(self)
                except Exception as reprstyler_fail:
                    print(reprstyler_fail)
                    print('-- falling back to super...')
                    return super(HandyDict, self).__repr__()
            else:  # if reprstyler not set
                return super(HandyDict, self).__repr__()

    # turns out that these two methods are essential to enable pickling of this object
    #  https://stackoverflow.com/questions/2049849/why-cant-i-pickle-this-object
    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)


# ==== REPR styling functions =====
def reprstyler_basic(subject=None):
    txt = 'keys:'
    for key in subject.keys():
        if key == 'reprstyler' or key == 'reprstyler_html':  # do not list reprstyler
            continue
        txt = f"{txt}'{key}', "
    return txt


def reprstyler_basic_html(subject=None):
    txt = ''
    if 'type' in subject.keys():
        txt = f'{txt}<em>Type:</em> {subject.type}; '
    if 'name' in subject.keys():
        txt = f'{txt}<em>Name:</em> {subject.name}; '
    txt = f'{txt}<br/>'
    txt = f'{txt}<table><tr><th>key</th><th>value</th></tr>'
    for key in subject.keys():
        if key == 'reprstyler' or key == 'reprstyler_html':  # do not list reprstyler
            continue
        # these two keys were listed already at the top:
        if key == 'type' or key == 'name':
            continue

        # begin row, display key name
        txt = f'{txt}<tr><td>{key}</td>'

        # display the content according to type
        if isinstance(subject[key], float):
            txt = f'{txt} <td> {subject[key]}</td>'
        elif isinstance(subject[key], int):
            txt = f'{txt} <td> {subject[key]}</td>'
        elif isinstance(subject[key], str):
            txt = f'{txt} <td> {subject[key]}</td>'
        elif _numpy_available and isinstance(subject[key], np.ndarray):
            txt = f'{txt} <td> np.array(shape={subject[key].shape}) </td>'
        elif _tensorflow_available and tf.is_tensor(subject[key]):
            txt = f'{txt} <td> tf tensor(shape={subject[key].shape}) </td>'
        else:  # any other type:
            txt = f'{txt} <td> {subject[key]} </td>'
        # end of table row
        txt = f'{txt} </tr> '
        # end for key in subject.keys()
    # end of html table
    txt = f'{txt} </table>'
    return txt


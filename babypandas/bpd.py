import pandas as pd


class DataFrame(object):
    '''
    Custom DataFrame Class; Pandas DataFrames with methods removed.

    :Example:
    >>> df = DataFrame.from_records([[1,2,3],[4,5,6]], columns=['a', 'b', 'c'])
    >>> df.shape
    (2, 3)
    >>> df.assign(d=[1,2]).shape
    (2, 4)
    >>> df.loc[1, 'b']
    5
    '''

    def __init__(self, **kwargs):
        
        # hidden pandas dataframe object
        self._pd = pd.DataFrame(**kwargs)
        
        # lift loc/iloc back to custom DataFrame objects
        self.loc = DataFrameIndexer(self._pd.loc)
        self.iloc = DataFrameIndexer(self._pd.iloc)

        # List of Pandas DataFrame methods to be made "public".
        _dunder_attrs = ['__str__', '__repr__', '_repr_html_']
        _props = ['shape', 'columns', 'index', 'values', 'T']
        _selection = ['take', 'drop', 'sample', 'get']
        _creation = ['assign']
        _transformation = ['apply', 'sort_values', 'describe', 'groupby']
        _combining = ['merge', 'append']
        _plotting = ['plot']
        _io = ['to_csv', 'to_numpy']
        
        _attrs = (
            _dunder_attrs + _props + _selection + 
            _creation + _transformation + _combining +
            _plotting + _io)

        for meth in _attrs:
            setattr(self, meth, _lift_to_pd(getattr(self._pd, meth)))

    # Formatting
    def __repr__(self):
        return self.__repr__()

    # return the underlying DataFrame
    def to_df(self):
        '''return the full pandas dataframe'''
        return self._pd
    
    # Creation
    @classmethod
    def from_dict(cls, data):
        return cls(data=data)
        
    @classmethod
    def from_records(cls, data, columns):
        
        return cls(data=data, columns=columns)


class Series(object):
    '''
    Custom Series class; Pandas Series with methods removed.
    '''

    def __init__(self, **kwargs):
        
        # hidden pandas dataframe object
        self._pd = pd.Series(**kwargs)
        
        # lift loc/iloc back to custom DataFrame objects
        self.loc = DataFrameIndexer(self._pd.loc)
        self.iloc = DataFrameIndexer(self._pd.iloc)

        # List of Pandas DataFrame methods to be made "public".
        _dunder_attrs = ['__str__', '__repr__']
        _props = ['shape']
        _selection = ['take', 'sample']
        _transformation = ['apply', 'sort_values', 'describe']
        _plotting = ['plot']
        _io = ['to_csv', 'to_numpy']
        
        _attrs = (
            _dunder_attrs + _props + _selection + 
            _transformation + _plotting + _io)

        for meth in _attrs:
            setattr(self, meth, _lift_to_pd(getattr(self._pd, meth)))

    # Formatting
    def __repr__(self):
        return self.__repr__()

    # return the underlying Series
    def to_ser(self):
        '''return the full pandas series'''
        return self._pd


class DataFrameGroupBy(object):
    '''
    '''

    def __init__(self, groupby):
        
        # hidden pandas dataframe object
        self._pd = groupby
        
        # List of Pandas methods to be made "public".
        _attrs = ['count', 'mean', 'median', 'min', 'max']

        for meth in _attrs:
            setattr(self, meth, _lift_to_pd(getattr(self._pd, meth)))

    # return the underlying groupby object
    def to_gb(self):
        '''return the full pandas dataframe'''
        return self._pd

    def aggregate(self, func):
        if not callable(func):
            raise Exception('Provide a function to aggregate')

        return self._pd.aggregate(func)
    

class DataFrameIndexer(object):
    '''
    Class for lifting results of loc/iloc back to the
    custom DataFrame class.
    '''
    def __init__(self, indexer):        
        self.idx = indexer
        
    def __getitem__(self, item):
        
        data = self.idx[item]
        if isinstance(data, pd.DataFrame):
            return DataFrame(data=self.idx[item])
        elif isinstance(data, pd.Series):
            return Series(self.idx[item])
        else:
            return data


def _lift_to_pd(func):
    '''checks output-type of function and if output is a
    Pandas object, lifts the output to a babypandas class'''

    if not callable(func):
        return func

    types = (DataFrame, DataFrameGroupBy, Series)

    def closure(*vargs, **kwargs):
        vargs = [x._pd if isinstance(x, types) else x for x in vargs]
        kwargs = {k: x._pd if isinstance(x, types) else x 
                  for (k, x) in kwargs.items()}

        a = func(*vargs, **kwargs)
        if isinstance(a, pd.DataFrame):
            return DataFrame(data=a)
        elif isinstance(a, pd.Series):
            return Series(data=a)
        elif isinstance(a, pd.core.groupby.generic.DataFrameGroupBy):
            return DataFrameGroupBy(a)
        else:
            return a

    closure.__doc__ = func.__doc__

    return closure


def read_csv(filepath, **kwargs):
    '''read_csv'''
    df = pd.read_csv(filepath, **kwargs)
    return DataFrame(data=df)
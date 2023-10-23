class DBConsts:
    CREATE_TABLE_FORMAT = \
        f'''
        (CatalogNumber INTEGER KEY, IsDigital INTEGER, ImageURL TEXT, Description TEXT, Info TEXT, UnitPrice REAL,
        NotRealUnitPrice REAL, inStock INTEGER, isCase INTEGER)
        '''

from core.orm import BoreholeOrm

class Project:
    def __init__(self, session):
        self.session = session
        self.refresh()
        #self.boreholes = None

    def refresh(self):
        self.boreholes = self.session.query(BoreholeOrm).all()

        
    def commit(self):
        self.session.commit()
        
    def add_borehole(self, bh):
        self.session.add(bh)
        self.commit()
        self.refresh()

    def row_count(self):
        return len(self.boreholes)

    def write_db(self):
        pass
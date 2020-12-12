from core.orm import BoreholeOrm

class Project:
    def __init__(self, session):
        self.session = session
        self.refresh()

    def refresh(self):
        self.boreholes = self.session.query(BoreholeOrm).all()
        
    def commit(self):
        self.session.commit()
        
    def add_borehole(self, bh):
        self.session.add(bh)
        self.commit()
        self.refresh()

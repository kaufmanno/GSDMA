from core.orm import BoreholeOrm, ComponentOrm


class Project:
    def __init__(self, session):
        self.session = session
        self.boreholes = None
        self.refresh()

    def refresh(self):
        self.boreholes = self.session.query(BoreholeOrm).all()
        
    def commit(self):
        self.session.commit()
        
    def add_borehole(self, bh):
        self.session.add(bh)
        self.commit()
        self.refresh()

    def add_components(self, components):
        for comp_id in components.keys():
            new_component = ComponentOrm(id=comp_id, description=components[comp_id].summary())
            self.session.add(new_component)
        self.commit()
        self.refresh()
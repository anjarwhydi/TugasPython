from ..models.admin import Admin

def checkUserEmailExist(email):
    admin = Admin.query.filter_by(email=email).first()

    if(admin):
        return True
    else:
        return False
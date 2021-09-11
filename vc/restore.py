from vc import create_app
from vc.db import db

if __name__ == '__main__':
    create_app()
    db.drop_all()
    db.create_all()

from . import db, BussinessModel

__all__ = ['Databases']


class Databases(BussinessModel):
    """ databases configure
    """
    dtype = db.Column(
        db.Text, nullable=False,
        comment='Database type, like mysql, postgresql'
    )
    name = db.Column(
        db.Text, nullable=False,
        comment='Database name'
    )
    ip = db.Column(
        db.Text, nullable=False,
        comment='Database IP address'
    )
    port = db.Column(
        db.Text, nullable=False,
        comment='Database port'
    )
    user = db.Column(
        db.Text, nullable=False,
        comment='Database user login'
    )
    password = db.Column(
        db.Text, nullable=False,
        comment='Database user password'
    )

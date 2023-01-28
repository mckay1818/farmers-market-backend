from app import db
from sqlalchemy.orm import relationship

class OrderProduct(db.Model):
    __tablename__ = 'order_product'
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), primary_key=True)
    # orders = relationship('Order', back_populates='order_details')
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    # products = relationship('Product', back_populates='order_details')
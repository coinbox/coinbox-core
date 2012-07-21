import app
from app.modules import Module

class ModuleLoader(Module):
    dependencies = ('base', 'currency')
    name = 'Products Inventory'

    def load(self):
        from app.modules.stock.objects.category import Category
        from app.modules.stock.objects.product import Product
        return [Category, Product]

    def test(self):
        from app.modules.stock.objects.category import Category
        from app.modules.stock.objects.product import Product
    
        session = app.database.session()
    
        cat1 = Category(name='Root1', parent=None)
        cat2 = Category(name='Sub1', parent=cat1)
        cat3 = Category(name='Sub2', parent=cat1)
        cat4 = Category(name='Sub2-Sub1', parent=cat3)
        cat5 = Category(name='Root2', parent=None)
    
        from app.modules.currency.objects.currency import Currency
        LL = session.query(Currency).filter_by(id=1).one()
        EUR = session.query(Currency).filter_by(id=3).one()
    
        p1 = Product(name='MAPED PENCILS 12-BOX', description='12 pencils box Maped', reference='ref123',
                     code='code123', price=1000, currency=LL, quantity=10, category=cat1)
        p2 = Product(name='MAPED SINGLE PENCIL', description='1 pencil Maped', reference='ref122',
                     code='code12345', price=250, currency=LL, quantity=20, category=cat2)
        p3 = Product(name='MAPED ERASER', description='Rounded Maped Eraser', reference='ref133',
                     code='code456', price=2, currency=EUR, quantity=5, category=cat3)
        p4 = Product(name='PHOTOCOPY B/W', description='Black and White Photocopy', reference='',
                     code='12345', price=250, currency=LL, quantity=None, category=cat4, in_stock=False)
        p5 = Product(name='ANNAHAR', description='An-Nahar Lebanese Daily Newspaper', reference='789',
                     code='barcode135', price=2000, currency=LL, quantity=None, category=cat5, in_stock=False)
    
        [session.add(p) for p in (p1, p2, p3, p4, p5)]
        session.commit()

    def menu(self):
        from app.modules.stock.pages import CategoriesPage
        from app.modules.stock.pages import ProductsPage
        from app.modules.stock.pages import StockDiaryPage
        
        return [[{'label': 'Stock', 'image': self.res('images/menu-stock.png')}],
                [{'parent': 'Stock', 'label': 'Products', 'page': ProductsPage, 'image': self.res('images/menu-products.png')},
                 {'parent': 'Stock', 'label': 'Categories', 'page': CategoriesPage, 'image': self.res('images/menu-categories.png')},
                 {'parent': 'Stock', 'label': 'Stock Diary', 'page': StockDiaryPage, 'image': self.res('images/menu-stock-diary.png')}]]

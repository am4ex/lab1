from abc import ABC, abstractmethod
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List

class InvalidPrice(Exception):
    def __init__(self, price):
        super().__init__(f"Error {price} Error")
        self.price = price

class Bookstore:
    def __init__(self, address: str, phone: str):
        self.address = address
        self.phone = phone
        self.books: list[Book] = []
        
    def add_book(self, book):
        self.books.append(book)

    def delete_book(self, book):
        self.books.remove(book)

    def get_book_by_title(self, title): 
        for b in self.books:
            if b.title == title:
                return b
        return None
    
    def update_book_price(self, title, new_price): 
        book = self.get_book_by_title(title)
        if book:
            book.price = new_price
            print(f"Цена книги '{title}' обновлена до {new_price}₽")
        else:
            print(f"Книга '{title}' не найдена.")

class Person:
    def __init__(self, id: int, name: str, phone: str):
        self.id = id
        self.name = name
        self.phone = phone
    
    def get_info(self):
        return f"{self.name}"


class Buyer(Person):
    def __init__(self, id: int, name: str, phone: str, email: str):
        super().__init__(id, name, phone)
        self.email = email

    def get_info(self):
        return f"{self.name} {self.email}"


class Employee(Person):
    def __init__(self, id: int, name: str, phone: str, position: str, salary: float, store=None):
        super().__init__(id, name, phone)
        self.position = position
        self.salary = salary

    def get_info(self):
        return f"{self.name} pos:{self.position}"
    
    
class Review:
    def __init__(self, buyer: Buyer, rating: int, comment: str):
        self.buyer = buyer
        self.rating = rating
        self.comment = comment

    def get_info(self):
        return f"{self.buyer} rat:{self.rating}"
  

class Author:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.books = []  

    def add_book(self, book):
        self.books.append(book)

    def get_info(self):
        info = f"Author: {self.name}"
        if self.books:
            info += "\nBooks:\n" + '\n'.join([b.title for b in self.books])
        return info


class Book(ABC):
    def __init__(self, id: int, title: str, author: Author, price: float):
        self.id = id
        self.title = title
        self.author = author
        self.price = price
        author.add_book(self)
        self.employees = []
        self.buyers = [] 
        self.reviews = []  
        
        if price <= 0:
            raise InvalidPrice(price)   

    @abstractmethod
    def get_info(self) -> str:
        pass

    def add_buyer(self, buyer: Buyer):
        self.buyers.append(buyer)
    
    def add_employee(self, employee: Employee):
        self.employees.append(employee)

    def add_review(self, review: Review):
        self.reviews.append(review)

    def delete_employee(self, employee: Employee):
        self.buyers.remove(employee)

    def delete_review(self, review: Review):
        self.buyers.remove(review)  

    def read_reviews(self):  # R
        if not self.reviews:
            print("Нет отзывов.")
        else:
            for r in self.reviews:
                print(f"{r.buyer.name}: {r.rating}/5 — {r.comment}")

    def update_price(self, new_price):  # U
        self.price = new_price  

    def get_info(self):
        info = f"Title: {self.title}\nAuthor: {self.author.name}\nPrice: {self.price}"
        if self.buyers:
            buyers_names = ', '.join([b.name for b in self.buyers])
            info += f"\nКупил(а): {buyers_names}"
        if self.employees:
            employee_names = ', '.join([e.name for e in self.employees])
            info += f"\nПродал(а): {employee_names}"
        if self.reviews:
            info += "\nReviews:"
            for r in self.reviews:
                info += f" - {r.buyer.name}: {r.rating}/5, {r.comment}"
        return info


class ChildrenBook(Book):
    def __init__(self, id: int, title: str, author: str, price: float, age_group: str):
        super().__init__(id, title, author, price)
        self.genre = "Children"
        self.age_group = age_group

    def get_info(self) -> str:
        base_info = super().get_info()
        return f"{self.title} ({self.age_group}) — {self.author.name}, {self.price}₽\n" + \
               base_info.split("\n", 1)[1]


class ScienceBook(Book):
    def __init__(self, id: int, title: str, author: str, price: float, field: str):
        super().__init__(id, title, author, price)
        self.genre = "Science"
        self.field = field

    def get_info(self) -> str:
        base_info = super().get_info()
        return f"{self.title} ({self.field}) — {self.author.name}, {self.price}₽\n" + \
               base_info.split("\n", 1)[1]


class FictionBook(Book):
    def __init__(self, id: int, title: str, author: str, price: float, subgenre: str):
        super().__init__(id, title, author, price)
        self.genre = "Fiction"
        self.subgenre = subgenre

    def get_info(self) -> str:
        base_info = super().get_info()
        return f"{self.title} ({self.subgenre}) — {self.author.name}, {self.price}₽\n" + \
               base_info.split("\n", 1)[1]


class EducationalBook(Book):
    def __init__(self, id: int, title: str, author: str, price: float, age_group: str):
        super().__init__(id, title, author, price)
        self.genre = "Educational"
        self.age_group = age_group

    def get_info(self) -> str:
        base_info = super().get_info()
        return f"{self.title} ({self.age_group}) — {self.author.name}, {self.price}₽\n" + \
               base_info.split("\n", 1)[1]


class DataManager:
    @staticmethod
    def save_to_json(bookstore, filename="bookstore.json"):
        data = {
            "bookstore": {
                "address": bookstore.address,
                "phone": bookstore.phone,
                "books": [DataManager.book_to_dict(b) for b in bookstore.books]
            }
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Данные сохранены в {filename}")

    @staticmethod
    def load_from_json(filename="bookstore.json"):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        store_data = data["bookstore"]
        bookstore = Bookstore(store_data["address"], store_data["phone"])
        for b_data in store_data["books"]:
            author = Author(b_data["author"]["id"], b_data["author"]["name"])
            genre = b_data.get("genre")
            if genre == "Children":
                book = ChildrenBook(b_data["id"], b_data["title"], author, b_data["price"], b_data.get("age_group", ""))
            elif genre == "Science":
                book = ScienceBook(b_data["id"], b_data["title"], author, b_data["price"], b_data.get("field", ""))
            elif genre == "Fiction":
                book = FictionBook(b_data["id"], b_data["title"], author, b_data["price"], b_data.get("subgenre", ""))
            elif genre == "Educational":
                book = EducationalBook(b_data["id"], b_data["title"], author, b_data["price"], b_data.get("age_group", ""))
            else:
                book = Book(b_data["id"], b_data["title"], author, b_data["price"])
            
            for b in b_data.get("buyers", []):
                buyer = Buyer(b["id"], b["name"], b["phone"], b.get("email",""))
                book.add_buyer(buyer)
            
            for e in b_data.get("employees", []):
                employee = Employee(e["id"], e["name"], e["phone"], e.get("position",""), e.get("salary",0))
                book.add_employee(employee)
            
            for r in b_data.get("reviews", []):
                buyer_data = r["buyer"]
                buyer = Buyer(buyer_data["id"], buyer_data["name"], buyer_data["phone"], buyer_data.get("email",""))
                review = Review(buyer, r["rating"], r["comment"])
                book.add_review(review)
            
            bookstore.add_book(book)
        print(f"Данные загружены из {filename}")
        return bookstore

    @staticmethod
    def book_to_dict(book):
        return {
            "id": book.id,
            "title": book.title,
            "price": book.price,
            "author": {"id": book.author.id, "name": book.author.name},
            "genre": getattr(book, "genre", ""),
            "age_group": getattr(book, "age_group", ""),
            "field": getattr(book, "field", ""),
            "subgenre": getattr(book, "subgenre", ""),
            "buyers": [{"id": b.id, "name": b.name, "phone": b.phone, "email": getattr(b, "email","")} for b in book.buyers],
            "employees": [{"id": e.id, "name": e.name, "phone": e.phone, "position": getattr(e,"position",""), "salary": getattr(e,"salary",0)} for e in book.employees],
            "reviews": [{"buyer": {"id": r.buyer.id, "name": r.buyer.name, "phone": r.buyer.phone, "email": getattr(r.buyer,"email","")}, "rating": r.rating, "comment": r.comment} for r in book.reviews]
        }

    @staticmethod
    def save_to_xml(bookstore, filename="bookstore.xml"):
        root = ET.Element("bookstore")
        ET.SubElement(root, "address").text = bookstore.address
        ET.SubElement(root, "phone").text = bookstore.phone
        books_elem = ET.SubElement(root, "books")

        for book in bookstore.books:
            book_elem = ET.SubElement(books_elem, "book", id=str(book.id))
            ET.SubElement(book_elem, "title").text = book.title
            ET.SubElement(book_elem, "price").text = str(book.price)
            
            author_elem = ET.SubElement(book_elem, "author", id=str(book.author.id))
            ET.SubElement(author_elem, "name").text = book.author.name
            
            if hasattr(book, "genre"): ET.SubElement(book_elem, "genre").text = book.genre
            if hasattr(book, "age_group"): ET.SubElement(book_elem, "age_group").text = book.age_group
            if hasattr(book, "field"): ET.SubElement(book_elem, "field").text = book.field
            if hasattr(book, "subgenre"): ET.SubElement(book_elem, "subgenre").text = book.subgenre
            
            buyers_elem = ET.SubElement(book_elem, "buyers")
            for b in book.buyers:
                b_elem = ET.SubElement(buyers_elem, "buyer", id=str(b.id))
                ET.SubElement(b_elem, "name").text = b.name
                ET.SubElement(b_elem, "phone").text = b.phone
                if hasattr(b, "email"): ET.SubElement(b_elem, "email").text = b.email
            
            employees_elem = ET.SubElement(book_elem, "employees")
            for e in book.employees:
                e_elem = ET.SubElement(employees_elem, "employee", id=str(e.id))
                ET.SubElement(e_elem, "name").text = e.name
                ET.SubElement(e_elem, "phone").text = e.phone
                if hasattr(e, "position"): ET.SubElement(e_elem, "position").text = e.position
                if hasattr(e, "salary"): ET.SubElement(e_elem, "salary").text = str(e.salary)
            
            reviews_elem = ET.SubElement(book_elem, "reviews")
            for r in book.reviews:
                r_elem = ET.SubElement(reviews_elem, "review")
                buyer_elem = ET.SubElement(r_elem, "buyer", id=str(r.buyer.id))
                ET.SubElement(buyer_elem, "name").text = r.buyer.name
                ET.SubElement(buyer_elem, "phone").text = r.buyer.phone
                if hasattr(r.buyer, "email"): ET.SubElement(buyer_elem, "email").text = r.buyer.email
                ET.SubElement(r_elem, "rating").text = str(r.rating)
                ET.SubElement(r_elem, "comment").text = r.comment
        
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_str)
        print(f"Данные сохранены в {filename}")

    @staticmethod
    def load_from_xml(filename="bookstore.xml"):
        tree = ET.parse(filename)
        root = tree.getroot()
        address = root.find("address").text
        phone = root.find("phone").text
        bookstore = Bookstore(address, phone)

        for book_elem in root.find("books").findall("book"):
            book_id = int(book_elem.attrib["id"])
            title = book_elem.find("title").text
            price = float(book_elem.find("price").text)
            
            author_elem = book_elem.find("author")
            author = Author(int(author_elem.attrib["id"]), author_elem.find("name").text)
            
            genre = book_elem.find("genre")
            age_group = book_elem.find("age_group")
            field = book_elem.find("field")
            subgenre = book_elem.find("subgenre")
            
            if genre is not None:
                if genre.text == "Children":
                    book = ChildrenBook(book_id, title, author, price, age_group.text if age_group else "")
                elif genre.text == "Science":
                    book = ScienceBook(book_id, title, author, price, field.text if field else "")
                elif genre.text == "Fiction":
                    book = FictionBook(book_id, title, author, price, subgenre.text if subgenre else "")
                elif genre.text == "Educational":
                    book = EducationalBook(book_id, title, author, price, age_group.text if age_group else "")
                else:
                    book = Book(book_id, title, author, price)
            else:
                book = Book(book_id, title, author, price)    
    
            for b_elem in book_elem.find("buyers").findall("buyer"):
                buyer = Buyer(int(b_elem.attrib["id"]), b_elem.find("name").text, b_elem.find("phone").text, b_elem.findtext("email",""))
                book.add_buyer(buyer)
            
            for e_elem in book_elem.find("employees").findall("employee"):
                employee = Employee(int(e_elem.attrib["id"]), e_elem.find("name").text, e_elem.find("phone").text,
                                    e_elem.findtext("position",""), float(e_elem.findtext("salary","0")))
                book.add_employee(employee)

            for r_elem in book_elem.find("reviews").findall("review"):
                b_elem = r_elem.find("buyer")
                buyer = Buyer(int(b_elem.attrib["id"]), b_elem.find("name").text, b_elem.find("phone").text, b_elem.findtext("email",""))
                rating = int(r_elem.find("rating").text)
                comment = r_elem.find("comment").text
                review = Review(buyer, rating, comment)
                book.add_review(review)
            
            bookstore.add_book(book)
        
        print(f"Данные загружены из {filename}")
        return bookstore


if __name__ == "__main__":

    author1 = Author(1, "Иванов")
    author2 = Author(2, "Петров")

    book1 = ChildrenBook(1, "Приключения", author1, 500, "7+")
    book2 = ScienceBook(2, "Физика", author2, 800, "Наука")

    buyer1 = Buyer(1, "Максим", "12345", "max@mail.com")
    buyer2 = Buyer(2, "Оля", "67890", "olya@mail.com")

    employee1 = Employee(1, "Петр", "54321", "Продавец", 2000)

    review1 = Review(buyer1, 5, "Отличная книга!")
    review2 = Review(buyer2, 4, "Неплохо, но сложно")

    book1.add_buyer(buyer1)
    book1.add_employee(employee1)
    book1.add_review(review1)

    book2.add_buyer(buyer2)
    book2.add_employee(employee1)
    book2.add_review(review2)

    store = Bookstore("ул. Примерная, 1", "+7 999 999 99 99")
    store.add_book(book1)
    store.add_book(book2)

    DataManager.save_to_json(store, "bookstore.json")
    DataManager.save_to_xml(store, "bookstore.xml")

    loaded_store_json = DataManager.load_from_json("bookstore.json")
    loaded_store_xml = DataManager.load_from_xml("bookstore.xml")

    for b in loaded_store_json.books:
        print(b.get_info())
        print("------")


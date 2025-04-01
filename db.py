import datetime
import json
class db_user:
    def __init__(self):
        with open('users.json', 'r') as file:
            self.data = json.load(file)
        self.authJson : dict= self.data['auth']
        self.admins : dict = self.data['admin']
        self.users : dict = self.data['user']
        

    def authenticate(self, username, password):
        if username and password:
            if username in self.authJson.keys() and self.authJson[username] == password:
                if username in self.admins:
                    user_role = 'admin'
                else:
                    user_role = 'user'
            else:
                user_role = 'guest'
        else:
            user_role = 'guest'
        
        return user_role
    
    def register(self, username, password):
        if username not in self.authJson.keys():
            self.authJson[username] = password
            self.users.append(username)
            with open('users.json', 'w') as file:
                json.dump(self.data, file, indent=4)
            return True
        else:
            return False
        
    def set_password(self, username, password):
        if username in self.authJson.keys():
            self.authJson[username] = password
            with open('users.json', 'w') as file:
                json.dump(self.data, file, indent=4)
            return True
        else:
            return False


    def delete_user(self, username):
        del self.authJson[username]
        with open('users.json', 'w') as file:
            json.dump(self.data, file, indent=4)
        return True


class db_book:
    def __init__(self):
        with open('bookInfo.json', 'r') as file:
            self.booksInfo :list= json.load(file)
        
        with open('bookAssets.json', 'r') as file:
            self.bookAsset :dict= json.load(file)
    
    def return_book(self, bookid):
        lib_book = self.bookAsset.get(bookid, None)
        lib_book['Due_date'] = None
        lib_book['borrow_by'] = None
        with open("bookAssets.json", "w") as file:
            json.dump(self.bookAsset, file, indent=4)

        return True
    
    def query_book_by(self, query_type, query, count, page):
        books = []
        skip = page * count - count

        for book in self.booksInfo:
            if len(books) >= count:
                break
            if query in book[query_type]:
                if skip > 0:
                    skip -= 1
                    continue
                books.append(book)
        if count == 0:
            total_pages = 1
        else:
            total_pages = len(self.booksInfo) // count + (1 if len(self.booksInfo) % count != 0 else 0)

        
        return books, total_pages
    
    def library_book_registry(self, isbn, book_id):
        isbn_exists = False
        for book in self.booksInfo:
            if isbn == book['isbn']:
                isbn_exists = True
                break

        if book_id not in self.bookAsset.keys() and isbn_exists:
            self.bookAsset[book_id] = {
                "isbn": isbn,
                "borrow_by": None,
                "Due_date": None
            }
            with open("bookAssets.json", "w") as file:
                json.dump(self.bookAsset, file, indent=4)

            return True
        else:
            return False
        
    def getAvailable_bookid(self, isbn):
        for book_id in self.bookAsset.keys():
            if self.bookAsset[book_id]['isbn'] == isbn and self.bookAsset[book_id]['borrow_by'] is None:
                return book_id
        return None

            


    def library_book_borrow(self, book_id, username):
        if book_id in self.bookAsset.keys():
            if self.bookAsset[book_id]['borrow_by'] is None:
                self.bookAsset[book_id]['borrow_by'] = username
                self.bookAsset[book_id]['Due_date'] = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
                with open("bookAssets.json", "w") as file:
                    json.dump(self.bookAsset, file, indent=4)
                return True, (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
            else:
                return False, 0
        else:
            return False, 0



        
    
    def addBook(self, title, author, publication_year, genre, isbn, pages, publisher, cover_image_url, rating, available):
        for book in self.booksInfo:
            if book['isbn'] == isbn:
                return False, 0
        if int(pages) <= 0:
            return False, 1
        if len(publication_year) != 4:
            return False, 2


        
        genre_list = genre.split(',')
        
        self.booksInfo.append({
            'title': title,
            'author': author,
            'publication_year': publication_year,
            'genre': genre_list,
            'isbn': isbn,
            'pages': pages,
            'publisher': publisher,
            'cover_image_url': cover_image_url,
            'rating': rating,
            'available': available
        })
        with open('books.json', 'w') as file:
            json.dump(self.booksInfo, file, indent=4)
        return True, -1
    
    def deleteBook(self, isbn):
        for book in self.booksInfo:
            if book['isbn'] == isbn:
                self.booksInfo.remove(book)
                with open('books.json', 'w') as file:
                    json.dump(self.booksInfo, file, indent=4)
                return True
        return False

    
    def editBook(self, title, author, publication_year, genre, isbn, pages, publisher, cover_image_url, rating, available):
        if int(pages) <= 0:
            return False, 1
        if len(publication_year) != 4:
            return False, 2


        
        genre_list = genre.split(',')
        
        self.booksInfo.append({
            'title': title,
            'author': author,
            'publication_year': publication_year,
            'genre': genre_list,
            'isbn': isbn,
            'pages': pages,
            'publisher': publisher,
            'cover_image_url': cover_image_url,
            'rating': rating,
            'available': available
        })
        with open('books.json', 'w') as file:
            json.dump(self.booksInfo, file, indent=4)
        return True, -1
if __name__ == '__main__':
    db_books = db_book()
    books = db_books.query_book_by('isbn', '978-0618260238', 10, 1)
    # print(books)
    print(db_books.deleteBook('123'))
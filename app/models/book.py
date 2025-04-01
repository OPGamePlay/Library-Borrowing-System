import datetime
import json
from pathlib import Path
from thefuzz import fuzz


class BookDB:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.books_path = self.base_dir / "data" / "books.json"
        self.assets_path = self.base_dir / "data" / "bookAssets.json"
        with self.books_path.open("r") as file:
            self.booksInfo: list = json.load(file)

        with self.assets_path.open("r") as file:
            self.bookAsset: dict = json.load(file)

    def return_book(self, bookid):
        lib_book = self.bookAsset.get(bookid, None)
        lib_book["Due_date"] = None
        lib_book["borrow_by"] = None
        with open("bookAssets.json", "w") as file:
            json.dump(self.bookAsset, file, indent=4)
        return True

    def query_book_by(self, query_type, query, count, page, use_fuzzy=False):
        if not query:
            skip = (page - 1) * count
            return self.booksInfo[skip : skip + count], len(self.booksInfo) // count + 1

        matching_books = []
        threshold = 65

        for book in self.booksInfo:
            matches = False

            if query_type == "title":
                if use_fuzzy:
                    score = fuzz.partial_ratio(query.lower(), book["title"].lower())
                    matches = score >= threshold
                else:
                    matches = query.lower() in book["title"].lower()

            elif query_type == "author":
                if use_fuzzy:
                    scores = [
                        fuzz.partial_ratio(query.lower(), author.lower())
                        for author in book["authors"]
                    ]
                    matches = any(score >= threshold for score in scores)
                else:
                    matches = any(
                        query.lower() in author.lower() for author in book["authors"]
                    )

            elif query_type == "categories":
                if use_fuzzy:
                    scores = [
                        fuzz.partial_ratio(query.lower(), category.lower())
                        for category in book["categories"]
                    ]
                    matches = any(score >= threshold for score in scores)
                else:
                    matches = any(
                        query.lower() in category.lower()
                        for category in book["categories"]
                    )

            elif query_type == "isbn":
                if use_fuzzy:
                    score = fuzz.partial_ratio(query.lower(), book["isbn"].lower())
                    matches = score >= threshold
                else:
                    matches = query in book["isbn"]

            if matches:
                matching_books.append(book)

        start_idx = (page - 1) * count
        end_idx = start_idx + count
        paginated_books = matching_books[start_idx:end_idx]

        total_pages = len(matching_books) // count + (
            1 if len(matching_books) % count != 0 else 0
        )
        if total_pages == 0:
            total_pages = 1

        return paginated_books, total_pages

    def library_book_registry(self, isbn, book_id):
        isbn_exists = False
        for book in self.booksInfo:
            if isbn == book["isbn"]:
                isbn_exists = True
                break

        if book_id not in self.bookAsset.keys() and isbn_exists:
            self.bookAsset[book_id] = {
                "isbn": isbn,
                "borrow_by": None,
                "Due_date": None,
            }
            with open("bookAssets.json", "w") as file:
                json.dump(self.bookAsset, file, indent=4)
            return True
        else:
            return False

    def getAvailable_bookid(self, isbn):
        for book_id in self.bookAsset.keys():
            if (
                self.bookAsset[book_id]["isbn"] == isbn
                and self.bookAsset[book_id]["borrow_by"] is None
            ):
                return book_id
        return None

    def library_book_borrow(self, book_id, username):
        if book_id in self.bookAsset.keys():
            if self.bookAsset[book_id]["borrow_by"] is None:
                self.bookAsset[book_id]["borrow_by"] = username
                self.bookAsset[book_id]["Due_date"] = (
                    datetime.datetime.now() + datetime.timedelta(days=7)
                ).strftime("%Y-%m-%d")
                with open("bookAssets.json", "w") as file:
                    json.dump(self.bookAsset, file, indent=4)
                return True, (
                    datetime.datetime.now() + datetime.timedelta(days=7)
                ).strftime("%Y-%m-%d")
            else:
                return False, 0
        else:
            return False, 0

    def addBook(
        self,
        title,
        authors,
        categories,
        isbn,
        pageCount,
        publishedDate,
        thumbnailUrl,
        shortDescription,
        longDescription,
    ):
        for book in self.booksInfo:
            if book["isbn"] == isbn:
                return False, 0
        if int(pageCount) <= 0:
            return False, 1

        # Generate a new _id
        max_id = max([book["_id"] for book in self.booksInfo]) if self.booksInfo else 0
        new_id = max_id + 1

        # Convert authors and categories to lists if they're strings
        if isinstance(authors, str):
            authors = [author.strip() for author in authors.split(",")]
        if isinstance(categories, str):
            categories = [category.strip() for category in categories.split(",")]

        new_book = {
            "_id": new_id,
            "title": title,
            "isbn": isbn,
            "pageCount": pageCount,
            "publishedDate": {
                "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000-0700")
            },
            "thumbnailUrl": thumbnailUrl,
            "shortDescription": shortDescription,
            "longDescription": longDescription,
            "authors": authors,
            "categories": categories,
        }

        self.booksInfo.append(new_book)
        with open("books.json", "w") as file:
            json.dump(self.booksInfo, file, indent=4)
        return True, -1

    def deleteBook(self, isbn):
        for book in self.booksInfo:
            if book["isbn"] == isbn:
                self.booksInfo.remove(book)
                with open("books.json", "w") as file:
                    json.dump(self.booksInfo, file, indent=4)
                return True
        return False

    def editBook(
        self,
        book_id,
        title,
        authors,
        categories,
        isbn,
        pageCount,
        publishedDate,
        thumbnailUrl,
        shortDescription,
        longDescription,
    ):
        if int(pageCount) <= 0:
            return False, 1

        # Convert authors and categories to lists if they're strings
        if isinstance(authors, str):
            authors = [author.strip() for author in authors.split(",")]
        if isinstance(categories, str):
            categories = [category.strip() for category in categories.split(",")]

        for i, book in enumerate(self.booksInfo):
            if book["_id"] == book_id:
                self.booksInfo[i] = {
                    "_id": book_id,
                    "title": title,
                    "isbn": isbn,
                    "pageCount": pageCount,
                    "publishedDate": book["publishedDate"],
                    "thumbnailUrl": thumbnailUrl,
                    "shortDescription": shortDescription,
                    "longDescription": longDescription,
                    "authors": authors,
                    "categories": categories,
                }
                with open("books.json", "w") as file:
                    json.dump(self.booksInfo, file, indent=4)
                return True, -1
        return False, 0


db_book = BookDB()

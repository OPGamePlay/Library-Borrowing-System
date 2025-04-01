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

    def get_borrowed_book(self, book_id, isbn):
        book_id = str(book_id)

        if book_id not in self.bookAsset:
            return None, None

        book_asset = self.bookAsset[book_id]
        if book_asset["isbn"] != isbn:
            return None, None

        if book_asset["borrow_by"] is None:
            return None, None

        return book_id, book_asset

    def return_book(self, book_id, isbn):
        assets_id, _ = self.get_borrowed_book(book_id, isbn)
        if assets_id is None:
            return False

        self.bookAsset[assets_id]["due_date"] = None
        self.bookAsset[assets_id]["borrow_by"] = None
        with self.assets_path.open("w") as file:
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
                book_title = book.get("title", "")
                if use_fuzzy:
                    score = fuzz.partial_ratio(query.lower(), book_title.lower())
                    matches = score >= threshold
                else:
                    matches = query.lower() in book_title.lower()

            elif query_type == "author":
                book_authors = book.get("authors", [])
                if use_fuzzy:
                    scores = [
                        fuzz.partial_ratio(query.lower(), author.lower())
                        for author in book_authors
                    ]
                    matches = any(score >= threshold for score in scores)
                else:
                    matches = any(
                        query.lower() in author.lower() for author in book_authors
                    )

            elif query_type == "categories":
                book_categories = book.get("categories", [])
                if use_fuzzy:
                    scores = [
                        fuzz.partial_ratio(query.lower(), category.lower())
                        for category in book_categories
                    ]
                    matches = any(score >= threshold for score in scores)
                else:
                    matches = any(
                        query.lower() in category.lower()
                        for category in book_categories
                    )

            elif query_type == "isbn":
                book_isbn = book.get("isbn", "")
                if use_fuzzy:
                    score = fuzz.partial_ratio(query.lower(), book_isbn.lower())
                    matches = score >= threshold
                else:
                    matches = query in book_isbn
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

    def getAvailable_bookid(self, isbn):
        isbn_exists = False
        for book_id, book_asset in self.bookAsset.items():
            if book_asset["isbn"] == isbn:
                isbn_exists = True
                # If we find an available copy, return its ID
                if book_asset["borrow_by"] is None:
                    return book_id

        if not isbn_exists:
            new_id = str(max([int(id) for id in self.bookAsset.keys()], default=0) + 1)
            self.bookAsset[new_id] = {"isbn": isbn, "borrow_by": None, "due_date": None}
            # Save the updated bookAssets
            with self.assets_path.open("w") as file:
                json.dump(self.bookAsset, file, indent=4)
            return new_id

        return None

    def library_book_borrow(self, book_id, username):
        if book_id in self.bookAsset.keys():
            if self.bookAsset[book_id]["borrow_by"] is None:
                self.bookAsset[book_id]["borrow_by"] = username
                self.bookAsset[book_id]["due_date"] = (
                    datetime.datetime.now() + datetime.timedelta(days=7)
                ).strftime("%Y-%m-%d")
                with self.assets_path.open("w") as file:
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
            book_isbn = book.get("isbn", "")
            if book_isbn == isbn:
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
            "publishedDate": {"date": publishedDate},
            "thumbnailUrl": thumbnailUrl,
            "shortDescription": shortDescription,
            "longDescription": longDescription,
            "authors": authors,
            "categories": categories,
        }

        self.booksInfo.append(new_book)
        with self.books_path.open("w") as file:
            json.dump(self.booksInfo, file, indent=4)

        self.bookAsset[str(new_id)] = {
            "isbn": isbn,
            "borrow_by": None,
            "due_date": None,
        }
        with self.assets_path.open("w") as file:
            json.dump(self.bookAsset, file, indent=4)
        return True, -1

    def deleteBook(self, isbn):
        for book in self.booksInfo:
            if book["isbn"] == isbn:
                self.booksInfo.remove(book)
                with self.books_path.open("w") as file:
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
        if isinstance(authors, str):
            authors = [author.strip() for author in authors.split(",")]
        if isinstance(categories, str):
            categories = [category.strip() for category in categories.split(",")]
        if isinstance(book_id, str):
            book_id = int(book_id)

        for i, book in enumerate(self.booksInfo):
            if book["_id"] == book_id:
                self.booksInfo[i] = {
                    "_id": book_id,
                    "title": title,
                    "isbn": isbn,
                    "pageCount": pageCount,
                    "publishedDate": publishedDate,
                    "thumbnailUrl": thumbnailUrl,
                    "shortDescription": shortDescription,
                    "longDescription": longDescription,
                    "authors": authors,
                    "categories": categories,
                }
                with self.books_path.open("w") as file:
                    json.dump(self.booksInfo, file, indent=4)
                asset_id = str(book_id)
                if asset_id in self.bookAsset:
                    self.bookAsset[asset_id]["isbn"] = isbn
                    with self.assets_path.open("w") as file:
                        json.dump(self.bookAsset, file, indent=4)

                return True, -1
        return False, 0


db_book = BookDB()

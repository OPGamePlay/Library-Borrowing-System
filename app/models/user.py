import json
from pathlib import Path


class UserDB:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.users_path = self.base_dir / "data" / "users.json"
        with self.users_path.open("r") as file:
            self.data = json.load(file)
        self.authJson: dict = self.data["auth"]
        self.admins: dict = self.data["admin"]
        self.users: list = self.data["user"]

    def authenticate(self, username, password):
        if username and password:
            if username in self.authJson.keys() and self.authJson[username] == password:
                if username in self.admins:
                    user_role = "admin"
                else:
                    user_role = "user"
            else:
                user_role = "guest"
        else:
            user_role = "guest"

        return user_role

    def register(self, username, password):
        if username not in self.authJson.keys():
            self.authJson[username] = password
            self.users.append(username)
            with self.users_path.open("w") as file:
                json.dump(self.data, file, indent=4)
            return True
        else:
            return False

    def set_password(self, username, password):
        if username in self.authJson.keys():
            self.authJson[username] = password
            with self.users_path.open("w") as file:
                json.dump(self.data, file, indent=4)
            return True
        else:
            return False

    def delete_user(self, username):
        del self.authJson[username]
        with self.users_path.open("w") as file:
            json.dump(self.data, file, indent=4)
        return True


db_user = UserDB()

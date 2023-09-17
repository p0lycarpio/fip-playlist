import json

import requests


class RadioFrance:
    base_url = "https://www.radiofrance.fr"
    api_path = "bibliotheque/api/playlists"

    def __init__(self, email, password, user_id=None):
        self.email = email
        self.password = password
        self.boundary = "011000010111000001101001"

        self.user_id: str = user_id
        self.user_token: str = ""
        self.refresh_token: str = ""

        self.headers: dict = {"accept": "application/json", "accept-charset": "utf-8"}
        self.__login()

    def __update_headers(self, new_header: dict):
        self.headers.update(new_header)

    def __login(self) -> str:
        url = f"{self.base_url}/auth"
        querystring = {"/login": ""}
        payload = f'-----{self.boundary}\r\nContent-Disposition: form-data; name="mail"\r\n\r\n{self.email}\r\n-----{self.boundary}\r\nContent-Disposition: form-data; name="password"\r\n\r\n{self.password}\r\n-----{self.boundary}--\r\n'
        headers = {
            "accept": "application/json",
            "content-type": f"multipart/form-data; boundary=---{self.boundary}",
            "origin": self.base_url,
        }
        response = requests.request(
            "POST", url, data=payload, headers=headers, params=querystring
        )

        response = response.json()
        data = json.loads(response["data"])
        self.user_id = data[1]
        self.user_token = data[2]
        self.refresh_token = data[3]
        self.__update_headers(
            {
                "x-user-id": self.user_id,
                "x-user-token": self.user_token,
                "x-user-refresh-token": self.refresh_token,
            }
        )

        return data

    def __refresh_token(self):
        url = f"{self.base_url}/api/v2.1/me/refresh-token"
        response = requests.request("POST", url, headers=self.headers)
        if response.status_code != 200:
            return

        response = response.json()
        self.user_token = response["token"]
        self.refresh_token = response["refreshToken"]

    def get_playlist(self, kind: str = "FAVORITE") -> str:
        url = f"{self.base_url}/{self.api_path}/playlists"

        response = requests.request("GET", url, headers=self.headers)

        if response.status_code == 401:
            self.__refresh_token()
            return self.get_playlist()
        elif response.status_code != 200:
            print(f"radiofrance.getPlaylist() : Error {response.status_code}")
        else:
            response = response.json()
            matches = [
                playlist["id"]
                for playlist in response.get("playlists", [])
                if playlist.get("kind") == kind
            ]
            return matches[0] if matches else None

    def get_playlist_items(
        self, playlist_id: str, t_from: int = None, short: bool = True
    ) -> list:
        url = f"{self.base_url}/{self.api_path}/items"
        querystring = {"playlistId": playlist_id, "minEventAt": t_from}

        response = requests.request(
            "GET", url, headers=self.headers, params=querystring
        )
        if response.status_code == 401 | 403:
            self.__refresh_token()
            return self.get_playlist_items()
        elif response.status_code != 200:
            print(f"radiofrance.getPlaylistItems() : Error {response.status_code}")
        else:
            response = response.json()
            # print(f"{len(response['items'])} items retrieved")
            if short:
                return [
                    song["id"] for song in response["items"] if song["isActive"] == True
                ]
            else:
                return response["items"]

    def get_tracks_uri(self, ids: list) -> tuple[list, list]:
        if not ids:
            return ([], [])

        url = f"{self.base_url}/{self.api_path}/items/details"
        querystring = {"ids": ",".join(ids), "model": "SONG"}

        response = requests.request(
            "GET", url, headers=self.headers, params=querystring
        )

        if response.status_code == 200:
            response = response.json()
            print("get tracks uri response", response)

            uris = [
                link["url"].split("/")[-1]
                for item in response.get("items", [])
                for link in item.get("links", [])
                if link.get("label") == "spotify"
            ]

            orphans = []
            for song in response["items"]:
                if not any(link["label"] == "spotify" for link in song["links"]):
                    orphans.append(song)

            return (uris, orphans)

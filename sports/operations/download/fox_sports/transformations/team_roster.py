class Transformer:
    __slots__ = ("team_meta", "headers_columns", "player_meta", "meta")

    def __init__(self, team_meta=None, headers_columns=None, meta=None):
        self.team_meta = team_meta or {}
        self.headers_columns = headers_columns or []
        self.player_meta = {}
        self.meta = meta or {}

    def parse_player_data(self, data):
        columns = data["columns"]
        n = len(columns)
        player_id = data["entityLink"]["layout"]["tokens"]["id"]
        self.player_meta = {"player_id": player_id, "player": columns[0]["text"]}
        for i in range(1, n):
            player_data = {"attribute": self.headers_columns[i]["text"].lower().strip(), "value": columns[i]["text"]}
            yield {**self.meta, **self.team_meta, **self.player_meta, **player_data}

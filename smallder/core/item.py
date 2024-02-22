class Item(dict):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = Item(value)









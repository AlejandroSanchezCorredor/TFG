class Data:
    def clear(self):
        keys = list(vars(self).keys())
        for key in keys:
            delattr(self, key)


current_task = Data()

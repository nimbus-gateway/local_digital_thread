class YourClass:
    def __init__(self):
        self.data_sources = {}

    def add_dynamic_key(self, key, value):
        # The key is provided at runtime
        self.data_sources[key] = value

# Example usage:
instance = YourClass()
dynamic_key = "some_dynamic_key"
dynamic_value = "some_value"

# Add the dynamically determined key and value
instance.add_dynamic_key(dynamic_key, dynamic_value)


print(instance.data_sources)
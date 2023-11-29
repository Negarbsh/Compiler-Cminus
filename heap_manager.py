class HeapManager:

    def __init__(self):

        # Initialize the address for the first free memory location in the heap.
        self.first_free = 500

        # Dictionary to store variables with their memory addresses as keys.
        self.variables = {}

        # heap manager is called twice for arrays. firstly with the declare_id and secondly
        # with modify attributes. after the second call with have to modify array type for address of array.
        # last_assigned is used for this.
        
        # Used to track the last temporary variable created, especially for arrays.
        self.last_temp = None

    def get_temp(self, type_name, size=1, array_attribute=False):
        """
        Allocate memory for a temporary variable and return its address.

        :param type_name: The data type of the variable (e.g., 'int').
        :param size: The number of memory units to allocate (default is 1).
        :param array_attribute: Boolean indicating if the variable is an array.
        :return: Address of the first free cell allocated for this variable.
        """
        # Store the starting address of the allocated memory.
        temp_address = self.first_free

        # If the variable is an array, append '-arr' to its type name.
        if array_attribute:
            self.last_temp.type_name += "-arr"

        # Allocate memory units based on the size and update the first free address.
        for i in range(size):
            temp = TempVariable(type_name, self.first_free, array_attribute)
            self.variables[self.first_free] = temp
            self.first_free += self.get_length_by_type(type_name)
            self.last_temp = temp

        return temp_address

    @staticmethod
    def get_length_by_type(type_name):
        if type_name == "int":
            return 4
        elif type_name == "void":
            return 1

    def get_type_by_address(self, address):
        return self.variables[address].type_name

class TempVariable:
    def __init__(self, type_name, address, array_attribute):
        self.type_name = type_name
        self.address = address
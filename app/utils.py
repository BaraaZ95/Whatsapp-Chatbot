def expect(input, expectedType):
    if isinstance(input, expectedType):
        return True
    else:
        return False

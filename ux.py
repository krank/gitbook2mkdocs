import builtins

visible:bool = True

#TODO: Add more granular verbosity for debug messages
#TODO: Use logger?

def set_visible(s: bool):
    global visible
    visible = s

def header(text: str):
    print('\n################################################################################')
    print(f'   {text}')
    print('--------------------------------------------------------------------------------')

def print(text: str):
    if visible:
        builtins.print(text)
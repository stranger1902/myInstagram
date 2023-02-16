import json

class MyInstagramException(Exception):

    def __init__(self, msg):
        
        if msg:
            
            if isinstance(msg, str): self.message = msg

            elif isinstance(msg, dict) or isinstance(msg, list): self.message = "\n" + json.dumps(msg, indent=4)

            else: self.message = None

        else: self.message = None

    def __str__(self): return self.message if self.message else "MyInstagramException has been raised"

class MyTypeException(Exception):

    def __init__(self, msg):
        
        if msg:

            if isinstance(msg, str): self.message = msg

            elif isinstance(msg, dict) or isinstance(msg, list): self.message = "\n" + json.dumps(msg, indent=4)

            else: self.message = None

        else: self.message = None

    def __str__(self): return self.message if self.message else "MyTypeException has been raised"

class MyLoginException(Exception):

    def __init__(self, msg):
        
        if msg:

            if isinstance(msg, str): self.message = msg

            elif isinstance(msg, dict) or isinstance(msg, list): self.message = "\n" + json.dumps(msg, indent=4)

            else: self.message = None

        else: self.message = None

    def __str__(self): return self.message if self.message else "MyLoginException has been raised"

class MyLoginRequiredException(Exception):

    def __init__(self, msg):
        
        if msg:

            if isinstance(msg, str): self.message = msg

            elif isinstance(msg, dict) or isinstance(msg, list): self.message = "\n" + json.dumps(msg, indent=4)

            else: self.message = None

        else: self.message = None

    def __str__(self): return self.message if self.message else "MyLoginRequiredException has been raised"

class MyDatabaseException(Exception):

    def __init__(self, msg):
        
        if msg:

            if isinstance(msg, str): self.message = msg

            elif isinstance(msg, dict) or isinstance(msg, list): self.message = "\n" + json.dumps(msg, indent=4)

            else: self.message = None

        else: self.message = None

    def __str__(self): return self.message if self.message else "MyDatabaseException has been raised"

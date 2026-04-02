from unicodedata import name

def check_any(*funcs):
    def combined(user):
        return any(f(user) for f in funcs)
    return combined

def check_client(user):
    if user.is_superuser:
        return True
    return user.groups.filter(name="Client").exists() 

def check_trainer(user):
    if user.is_superuser:
        return True
    return user.groups.filter(name="Trainer").exists()

def check_student(user):
    if user.is_superuser:
        return True
    return user.groups.filter(name="Student").exists()


def check_knowinmy(user):
    if user.is_superuser:
        return True
    return user.groups.filter(name="Knowinmy").exists()

def check_superuser(user):
    return user.is_superuser
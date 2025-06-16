import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, self) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
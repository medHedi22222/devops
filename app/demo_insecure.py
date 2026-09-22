"""
DEMO ONLY — insecure patterns for Semgrep/Bandit. Do not merge to master.
"""

def dangerous_eval(user_input):
    # code injection
    return eval(user_input)

def dangerous_exec(user_input):
    exec(user_input)

def hardcoded_password():
    password = "SuperSecretPassword123"
    return password

def weak_hash():
    import hashlib
    return hashlib.md5(b"data").hexdigest()

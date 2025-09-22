import re, os, string, base64

NOTES_DIR = "notes/"

if not os.path.isdir(NOTES_DIR):
    os.mkdir(NOTES_DIR)

def valid_uuid(string):
    return re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", string)

def sanitize_filename(filename):
    length = len(filename)
    for i in range(length):
        char = filename[i]
        if char not in string.ascii_letters + string.digits:
            filename = filename.replace(char, "XX")
    return filename

def read_note(uuid, name):
    if not valid_uuid(uuid):
        return False, "Invalid UUID"
    base = os.path.join(NOTES_DIR, uuid)
    name = sanitize_filename(name)
    note_path = os.path.join(base, name)
    if os.path.commonpath([base, note_path]) != base:
        return False, "You can't do that here"
    if not os.path.isfile(note_path):
        return False, "Note doesn't exist"
    with open(note_path, "r") as f:
        return True, f.read()
    
def list_notes(uuid):
    if not valid_uuid(uuid):
        return False, "Invalid UUID"
    base = os.path.join(NOTES_DIR, uuid)
    if not os.path.isdir(base):
        return False, "User doesn't exist"
    return True, os.listdir(base)

def write_note(uuid, name, data):
    if not valid_uuid(uuid):
        return False, "Invalid UUID"
    base = os.path.join(NOTES_DIR, uuid)
    name = sanitize_filename(name)
    note_path = os.path.join(base, name)
    if os.path.commonpath([base, note_path]) != base:
        return False, "You can't do that here"
    if os.path.isfile(note_path):
        return False, "Note already exists!"

    if not os.path.exists(base):
        os.mkdir(base)
    
    b64ed = base64.b64encode(data.encode()).decode()

    os.system(f"echo {b64ed} | base64 -d > {note_path}")

    return True, name